import time
import json
import os
from urllib.parse import urlparse
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def get_driver(profile_path, headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    # Attach your real Waterfox/Firefox profile
    profile = FirefoxProfile(profile_path)
    options.profile = profile  # ← this is the correct way now

    service = Service(executable_path="/usr/bin/geckodriver") #directory of geckodriver on linux
    return webdriver.Firefox(service=service, options=options)


def load_firefox_profile(path="ff-profile.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        data = json.load(f)

    ffprofile = data.get("ffprofile")
    if not ffprofile:
        raise ValueError("Firefox profile path not found in ff-profile.json")

    return ffprofile


def tester():
    PROFILE_PATH = load_firefox_profile()
    driver = get_driver(PROFILE_PATH, headless=False)
    driver.get("https://www.saatchiart.com/")
    print(driver.title)
    input("Press Enter to quit...")
    driver.quit()


def load_secrets(platform_name, path="secrets.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        all_secrets = json.load(f)

    for entry in all_secrets:
        if entry.get("platform", "Saatchi-Art").lower() == platform_name.lower():
            return entry

    raise ValueError(f"No credentials found for platform: {platform_name}")


def load_catalog(path="saatchi-art-catalog.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        return json.load(f)


def get_artwork_by_id(artworks, target_id):
    for art in artworks:
        if art.get("id") == target_id:
            return art
    raise ValueError(f"No artwork found with id {target_id}")


def logIN(driver, email, password, timeout=15):
    driver.get("https://www.saatchiart.com/authentication")

    wait = WebDriverWait(driver, timeout)

    time.sleep(1.5)

    # Wait for email input
    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
    time.sleep(0.5)
    email_input.clear()
    email_input.send_keys(email)

    # Wait for password input
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
    time.sleep(0.5)
    password_input.clear()
    password_input.send_keys(password)

    # Click submit button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(0.5)
    login_button.click()

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[class*='Account_accountIconInitials']")))
        print("✅ Login successful.")
        return True
    except:
        print("❌ Login may have failed or needs manual intervention.")
        return False


def go_to_upload_form(driver, timeout=15):
    upload_url = "https://www.saatchiart.com/studio/upload"
    driver.get(upload_url)
    
    try:
        time.sleep(0.5)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="title"]'))  # or any upload form field
        )
        time.sleep(0.5)
        print("[go_to_upload_form] Upload form is ready.")
    except Exception as e:
        print(f"[go_to_upload_form] Failed to load upload form: {e}")


def is_logged_in(driver):
    try: 
        driver.find_element(By.CSS_SELECTOR, "span[class*='Account_accountIconInitials']")
        return True
    except NoSuchElementException:
        return False


def setUp(platform="Saatchi-Art", headless=False):
    PROFILE_PATH = load_firefox_profile()
    driver = get_driver(profile_path=PROFILE_PATH, headless=headless)

    secrets = load_secrets(platform)
    EMAIL = secrets["email"]
    PASSWORD = secrets["password"]

    if not is_logged_in(driver):
        logIN(driver, EMAIL, PASSWORD)

    return driver
    



def upload_artwork(driver, artwork_id):
    artworks = load_catalog()
    art = get_artwork_by_id(artworks, artwork_id)

    return True


def main():
        driver = setUp()
        go_to_upload_form(driver)


if __name__ == "__main__":
    main()


