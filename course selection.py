import time
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================
# Configurable constants
# ==============================

RETRY_INTERVAL = 30                    # seconds between attempts
PAGE_LOAD_TIMEOUT = 20                 # seconds
CRN_BOX_PREFIX = "crn_id"               # typical IDs: crn_id1, crn_id2, ...
SUBMIT_BTN_XPATHS = [
    "//input[@type='submit' and contains(@value,'Submit')]",
    "//input[contains(@value,'Submit Changes')]",
]
CRN_PAGE_URL = "https://horizon.mcgill.ca/pban1/bwskfreg.P_AltPin"  # Add/Drop CRN page (Banner/Minerva)


# ==============================
# Helpers methods
# ==============================

def open_browser() -> webdriver.Chrome:
    """Launch Chrome via Selenium (standard automation)."""
    chrome_opts = Options()
    chrome_opts.add_experimental_option("detach", True)  # Keep browser open after script ends
    driver = webdriver.Chrome(options=chrome_opts)       # Selenium 4.6+ auto-manages ChromeDriver
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def on_crn_page(driver: webdriver.Chrome) -> bool:
    """Check if we are on the CRN entry form."""
    try:
        driver.find_element(By.ID, f"{CRN_BOX_PREFIX}1")
        return True
    except Exception:
        return False


def fill_crns_and_submit(driver: webdriver.Chrome, crns: List[str]) -> None:
    """Fill CRN fields and click Submit Changes."""
    for idx, crn in enumerate(crns, start=1):
        try:
            box = driver.find_element(By.ID, f"{CRN_BOX_PREFIX}{idx}")
            box.clear()
            box.send_keys(crn)
        except Exception:
            break  # No more boxes found

    for xp in SUBMIT_BTN_XPATHS:
        try:
            btn = driver.find_element(By.XPATH, xp)
            btn.click()
            return
        except Exception:
            continue
    raise RuntimeError("Could not find 'Submit Changes' button.")


def parse_registration_result(html: str, crns: List[str]) -> Tuple[List[str], List[str], bool]:
    """Parse HTML to find registered CRNs, failed CRNs, and session expiry."""
    soup = BeautifulSoup(html, "html.parser")

    # Detect expired session or login redirect
    title_text = (soup.title.get_text(strip=True) if soup.title else "").lower()
    body_text = soup.get_text(" ", strip=True).lower()
    session_expired = any(
        k in body_text for k in [
            "session expired", "session timeout", "please login again", "log in again", "enter your mcgill id"
        ]
    ) or "login" in title_text

    newly_registered = []
    failed = []

    tables = soup.find_all("table", class_="datadisplaytable")

    for t in tables:
        header_text = t.get_text(" ", strip=True).lower()
        if "registration add errors" in header_text:
            t_text = t.get_text(" ", strip=True)
            for crn in crns:
                if crn in t_text:
                    failed.append(crn)

    for t in tables:
        t_text = t.get_text(" ", strip=True).lower()
        if "registered" in t_text or "course reference number" in t_text:
            for crn in crns:
                if crn in t_text and crn not in newly_registered:
                    newly_registered.append(crn)

    return list(dict.fromkeys(newly_registered)), list(dict.fromkeys(failed)), session_expired


# ==============================
# Main
# ==============================
def main():
    print("=== McGill Auto Registration Script ===")
    print("Enter the CRNs you want to register (separated by spaces):")
    crns_input = input("> ").strip()
    if not crns_input:
        print("No CRNs entered. Exiting.")
        return

    crns = crns_input.split()
    print(f"\nYou entered {len(crns)} CRNs: {crns}")

    driver = open_browser()
    driver.get(CRN_PAGE_URL)

    input("\n Please log in to Minerva, go to the CRN entry page, then press Enter here to start... ")

    if not on_crn_page(driver):
        print("⚠ Could not detect CRN fields. Make sure you're on the Add/Drop CRN form.")
        input("Press Enter to continue anyway, or Ctrl+C to stop... ")

    remaining = crns.copy()

    try:
        while remaining:
            print(f"\n Submitting CRNs: {remaining}")

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, f"{CRN_BOX_PREFIX}1"))
                )
            except Exception:
                pass

            try:
                fill_crns_and_submit(driver, remaining)
            except Exception as e:
                print(f" Could not submit: {e}")
                time.sleep(RETRY_INTERVAL)
                continue

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            except Exception:
                time.sleep(2)

            html = driver.page_source
            newly_registered, failed, session_expired = parse_registration_result(html, remaining)

            if session_expired:
                print(" Session expired. Please log in again, then press Enter...")
                input()
                continue

            for crn in newly_registered:
                print(f" Registered: {crn}")
            for crn in failed:
                print(f" Error registering CRN {crn} (likely full/restricted).")

            remaining = [c for c in remaining if c not in newly_registered]

            if remaining:
                print(f" Retrying in {RETRY_INTERVAL} seconds...")
                time.sleep(RETRY_INTERVAL)

        print("\n All CRNs processed.")

    except KeyboardInterrupt:
        print("\n Stopped by user.")


if __name__ == "__main__":
    main()




