from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service

def getDriver(profile_path, headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    # Attach your real Waterfox/Firefox profile
    profile = FirefoxProfile(profile_path)
    options.profile = profile  # ← this is the correct way now

    service = Service(executable_path="/usr/bin/geckodriver") #directory of geckodriver on linux
    return webdriver.Firefox(service=service, options=options)

