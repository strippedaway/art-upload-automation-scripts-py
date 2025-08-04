import time
import json
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
    driver.get("https://www.artmajeur.com")
    print(driver.title)
    input("Press Enter to quit...")
    driver.quit()


def load_secrets(platform_name, path="secrets.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        all_secrets = json.load(f)

    for entry in all_secrets:
        if entry.get("platform", "Art-Majeur").lower() == platform_name.lower():
            return entry

    raise ValueError(f"No credentials found for platform: {platform_name}")


def load_catalog(path="art-majeur-catalog.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        return json.load(f)

def get_artwork_by_id(artworks, target_id):
    for art in artworks:
        if art.get("id") == target_id:
            return art
    raise ValueError(f"No artwork found with id {target_id}")


def logIN(driver, email, password, timeout=15):
    driver.get("https://www.artmajeur.com/en/login")

    wait = WebDriverWait(driver, timeout)

    time.sleep(3)

    # Wait for email input
    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
    time.sleep(1)
    email_input.clear()
    email_input.send_keys(email)

    # Wait for password input
    password_input = driver.find_element(By.ID, "password")
    driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
    time.sleep(1)
    password_input.clear()
    password_input.send_keys(password)

    # Click submit button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(1)
    login_button.click()

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/account']")))
        print("✅ Login successful.")
        return True
    except:
        print("❌ Login may have failed or needs manual intervention.")
        return False


def go_to_upload_form(driver, timeout=15):
    upload_url = "https://www.artmajeur.com/en/account/karen-terzyan/artworks/new"
    driver.get(upload_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "title"))  # or any upload form field
    )
    print("✅ Arrived at artwork upload form.")


def setUp(platform="Art-Majeur", headless=False):
    PROFILE_PATH = load_firefox_profile()
    driver = get_driver(profile_path=PROFILE_PATH, headless=headless)

    secrets = load_secrets(platform)
    EMAIL = secrets["email"]
    PASSWORD = secrets["password"]

    if not is_logged_in(driver):
        logIN(driver, EMAIL, PASSWORD)

    return driver
    


def uploadMain(driver, art):
    return True

def imageUpload(driver, art):
    return True

def autoComplete(driver, art):
    return True


def upload_artwork(driver, artwork_id):
    artworks = load_catalog()
    art = get_artwork_by_id(artworks, artwork_id)

    uploadMain(driver, art)
    imageUpload(driver, art)
    autoComplete(driver, art)



def main():
    driver = setUp()
    go_to_upload_form(driver)

    try:
        artwork_id = int(input("Enter the ID of the artwork to upload: "))
        upload_artwork(driver, artwork_id)
        print(f"✅ Successfully uploaded artwork ID {artwork_id}")
    except ValueError:
        print("❌ Invalid input. Please enter a numeric ID.")
    except Exception as e:
        print(f"❌ Upload failed: {e}")


    driver.quit()

if __name__ == "__main__":
    main()


