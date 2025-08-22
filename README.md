#Mcgill Course Registration Script 
#Description 
    -This program automatically tries to register for the CRNs provided for the user.

For non-programmers:
#Just download the .exe file and run it. 

    
For people with coding background:
#How-to
    -Having the prerequisite python libraries / softwares downloaded (see more below)
    -Log into minerva and go to the page of quick add/drop courses in remote-debugging mode on Chrome (instruction below)
    -Run the script 

#Prerequisite downloads / actions
    -Google Chrome
    -selenium (do pip install selenium on your command prompt) 
    -chromedriver：
        -check your chrome version(go to chrome://settings/help and note the version number )
        -go to https://googlechromelabs.github.io/chrome-for-testing/ and download the stable version that matches your chrome version
        -copy the ChromeDriver file path and add it to the System Path  
            -window + S --> search for "environment variables" --> open it --> click "edit the system environment variables" --> in the system properties window, click environment variables --> under system variables, find and select path --> click edit --> click new --> paste chromedriver file path.
    -BeautifulSoup:(do pip install beautifulsoup4 on your command prompt)
    -open chrome in remote-debugging mode:
        -copy the path of your Chrome(the one in your user file)
        -do "path to your chrome" --remote-debugging-port=9222 --user-data-dir="C:\chrome_profiles\mcgill_profile" on command prompt

    
      
