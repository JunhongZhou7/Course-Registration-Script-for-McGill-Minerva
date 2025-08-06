import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# --- Configuration ---
CRNS = ['2426', '3904']  # Replace with your CRNs
RETRY_INTERVAL = 30  # seconds

# --- Connect to existing Chrome session (remote debugging mode) ---
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=options)

# Wait for manual login and navigation
input("👉 Log in to Minerva and go to the CRN entry page. Press Enter when ready...")

# Track CRNs still unregistered
remaining_crns = CRNS.copy()

try:
    while remaining_crns:
        print(f"\n⏳ Attempting to register CRNs: {remaining_crns}")

        # Enter CRNs into the form
        for i, crn in enumerate(remaining_crns):
            try:
                input_box = driver.find_element(By.ID, f"crn_id{i+1}")
                input_box.clear()
                input_box.send_keys(crn)
            except Exception as e:
                print(f"⚠️ Could not enter CRN {crn}: {e}")

        # Submit form
        try:
            submit_btn = driver.find_element(By.XPATH, "//input[@value='Submit Changes']")
            submit_btn.click()
        except Exception as e:
            print("❌ Failed to click 'Submit Changes':", e)
            break

        time.sleep(3)  # Let the page reload

        # Use BeautifulSoup to parse the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        newly_registered = []
        registration_errors = []

        # 1. Check Current Schedule table for registered CRNs
        current_schedule_tables = soup.find_all('table', class_='datadisplaytable')
        for table in current_schedule_tables:
            if 'Course Reference Number' in table.text or 'Registered' in table.text:
                if any(crn in table.text for crn in remaining_crns):
                    for crn in remaining_crns:
                        if crn in table.text:
                            print(f"✅ CRN {crn} registered successfully.")
                            newly_registered.append(crn)

        # 2. Check for registration errors
        for table in current_schedule_tables:
            if 'Registration Add Errors' in table.text:
                for crn in remaining_crns:
                    if crn in table.text:
                        print(f"❌ CRN {crn} failed to register: registration error.")
                        registration_errors.append(crn)

        # 3. Check for unprocessed CRNs
        for crn in remaining_crns:
            if crn not in newly_registered and crn not in registration_errors:
                print(f"⚠️ CRN {crn}: status unknown — check manually.")

        # 4. Update CRNs list
        remaining_crns = [crn for crn in remaining_crns if crn not in newly_registered]

        if remaining_crns:
            print(f"🔁 Retrying in {RETRY_INTERVAL} seconds...\n")
            time.sleep(RETRY_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Stopped by user.")

finally:
    print("\n🎯 Finished. Remaining CRNs:", remaining_crns)


