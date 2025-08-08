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
from selenium.common.exceptions import ElementNotInteractableException

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


def load_catalog(platform_name):
    filename = f"{platform_name.lower()}-catalog.json"
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def load_fieldset(platform_name):
    filename = f"{platform_name.lower()}-fieldset.json"
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def get_content_by_id(catalog, target_id):
    for cnt in catalog.get("content", []):
        if cnt.get("id") == target_id:
            return cnt
    raise ValueError(f"No content found with id {target_id}")


def logIN(driver, secrets, fieldset, timeout=15):
    driver.get(secrets["address"])
    time.sleep(1)
    wait = WebDriverWait(driver, timeout)
    time.sleep(1.5)

    # Wait for email input
    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, secrets["email"]["field"])))
    time.sleep(0.5)
    driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
    time.sleep(0.5)
    email_input.clear()
    email_input.send_keys(secrets["email"]["value"])

    # Wait for password input
    password_input = driver.find_element(By.CSS_SELECTOR, secrets["password"]["field"])
    time.sleep(0.5)
    driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
    time.sleep(0.5)
    password_input.clear()
    password_input.send_keys(secrets["password"]["value"])

    # Click submit button
    login_button = driver.find_element(By.CSS_SELECTOR, secrets["button"])
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(0.5)
    login_button.click()


    is_logged_in(driver, fieldset, timeout=15)


def go_to_upload_form(driver, fieldset, timeout=15):
    upload_url = fieldset.get("upload_form")
    if not upload_url:
        raise ValueError("No 'upload_form' URL found in the fieldset.")
    
    driver.get(upload_url)
    
    input_test = fieldset.get(input_test)

    try:
        time.sleep(0.5)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, input_test))  # or any upload form field (must write check)
        )
        time.sleep(0.5)
        print("[go_to_upload_form] Upload form is ready.")
    except Exception as e:
        print(f"[go_to_upload_form] Failed to load upload form: {e}")


def is_logged_in(driver, fieldset):
    log_test = fieldset.get("log_test")
    try: 
        driver.find_element(By.CSS_SELECTOR, log_test)
        print("✅ Login successful.")
        return True
    except NoSuchElementException:
        print("❌ Login may have failed or needs manual intervention.")
        return False


def setUp(platform_name, catalog, headless=False):

    PROFILE_PATH = load_firefox_profile()
    
    driver = get_driver(profile_path=PROFILE_PATH, headless=headless)
    
    secrets = load_secrets(platform_name)

    catalog = load_catalog(platform_name)

    fieldset = load_fieldset(platform_name)
    
    if not is_logged_in(driver, catalog):
        logIN(driver, secrets, fieldset)

    return driver


def prepElem(driver, fieldset, content, fieldName, timeout=10):
    field_conf = fieldset.get(fieldName)
    if not field_conf:
                raise ValueError(f"[prepElem] No field mapping found for '{fieldName}'")

    selector = field_conf.get("selector")
   
    if not selector:
        raise ValueError(f"[prepElem] No selector defined in fieldset for '{fieldName}'")

    value = content.get(fieldName) if content and fieldName in content else None

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        time.sleep(0.5)

        element = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
        time.sleep(0.5)

        return element, value

    except Exception as e:
        print(f"[prepElem] ❌ Failed for field '{fieldName}': {e}")
        raise


def textFill(driver, content, fieldset, fieldName):
    try:
        element, value = prepElem(driver, fieldset, content, fieldName)
        element.clear()
        time.sleep(0.5)
        element.send_keys(value)

    except Exception as e:
        print(f"[textFill] ❌ Error filling text field: {e}")


def dropChoose(driver, fieldset, content, fieldName):
    try:
        element, value = prepElem(driver, fieldset, content, fieldName)
        Select(element).select_by_visible_text(value)

    except Exception as e:
        print(f"[dropChoose] ❌ Error choosing field: {e}")


def clickRadio(driver, content, fieldset, fieldName):
    try:
        element, _value = prepElem(driver, fieldset, content, fieldName)
        element.click()

    except Exception as e:
        print(f"[clickRadio] ❌ Error choosing field: {e}")


def clickMulti(driver, content, fieldset, fieldName):
    try:
        container, values = prepElem(driver, fieldset, content, fieldName)
    except Exception as e:
        print(f"[clickMulti] Could not prepare element for '{fieldName}': {e}")
        return
    
    if not values:
        print(f"[clickMulti] ⚠ No values provided for '{fieldName}'")
        return

    labels = container.find_elements(By.TAG_NAME, "label")

    for value in values:
        matched = False
        for label in labels:
            if value.lower() in label.text.lower():  # partial match
                try:
                    label.click()
                    matched = True
                    break
                except Exception as click_err:
                    print(f"[clickMulti] ❌ Could not click label '{label.text}': {click_err}")
        if not matched:
            print(f"[clickMulti] ⚠ No label matched '{value}' in '{fieldName}'")


def multiWordFill(driver, content, fieldset, fieldName):
    try:
        element, values = prepElem(driver, fieldset, content, fieldName)
    except Exception as e:
        print(f"[multiWordFill] ❌ Failed prep for '{fieldName}': {e}")
        return

    # Normalize value to a list
    if not values:
        print(f"[multiWordFill] ⚠ No values provided for '{fieldName}'")
        return
    elif isinstance(values, str):
        values = [values]
    elif not isinstance(values, list):
        print(f"[multiWordFill] ⚠ Invalid value format for '{fieldName}': {type(values)}")
        return

    # Determine what key to press after each word
    field_conf = fieldset.get(fieldName, {})
    submit_key_raw = field_conf.get("submitKey", "enter")  # original casing
    submit_key = submit_key_raw.lower()

    key = {
        "enter": Keys.ENTER,
        "comma": ",",
        "tab": Keys.TAB
    }.get(submit_key, Keys.ENTER)

    for word in values:
        try:
            element.send_keys(word)
            element.send_keys(key)
            time.sleep(0.2)
        except Exception as e:
            print(f"[multiWordFill] ⚠ Failed to enter '{word}' into '{fieldName}': {e}")


def clickButton(driver, content, fieldset, fieldName):
    try:
        button, _value, = prepElem(driver, fieldset, content, fieldName)

    except Exception as e:
        print(f"[clickButton] ❌ Failed to locate '{fieldName}': {e}")
        return

    try: 
        if button.is_displayed() and button.is_enabled():
            print(f"[clickButton] ✅ Clicked button for '{fieldName}'")
        else:
            print(f"[clickButton] ⚠ Button '{fieldName}' is not visible or enabled")
    except Exception as e:
        print(f"[clickButton] ❌ Error clicking '{fieldName}': {e}")


def prepImages(content, fieldset):
    base_path = content.get("image_directory", "")
    file_data = content.get("images", {})
    results = []

    # MAIN
    if "primary_image" in file_data and "primary_image" in fieldset:
        results.append({
            "is_main": True,
            "path": os.path.join(base_path, file_data["primary_image"]),
            "upload": fieldset["primary_image"]
        })

    # SECONDARY
    for key in sorted(file_data.keys()):
        if key.startswith("image") and key != "primary_image":
            try:
                index = int(key.replace("image", ""))
            except ValueError:
                continue

            image_path = os.path.join(base_path, file_data[key])
            upload_conf = fieldset.get("image")  # shared image selector
            if not upload_conf:
                continue  # no upload input defined

            entry = {
                "is_main": False,
                "path": image_path,
                "upload": upload_conf
            }

            caption_key = f"caption{index}"
            if caption_key in file_data and "caption" in fieldset:
                entry["caption"] = {
                    "value": file_data[caption_key],
                    **fieldset["caption"]  # shared caption field
                }

            results.append(entry)

    return results


def fileUpl(driver, image_path, fieldName):
    try:
        fieldName.send_keys(image_path)
        print(f"✅ Uploaded image: {image_path}")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"❌ Failed to upload image '{image_path}': {e}")
        # manualIntervention(driver, f"Could not upload {image_path}. Please upload manually.")
        return False


def uploadMainImage(driver, file_data):
    for file in file_data:
        if file.get("is_main"):
            path = file["path"]
            selector = file["upload"]["selector"]

            element = driver.find_element(By.CSS_SELECTOR, selector)

            fileUpl(driver, path, selector)
            break


def imageDesc(driver, caption, value):

    selector = caption["selector"]
    input_type = caption.get("type", "text").lower()

    element = driver.find_element(By.CSS_SELECTOR, selector)

    if input_type == "text":
        element.clear()
        time.sleep(0.5)
        element.send_keys(value)

    elif input_type == "dropdown":
        from selenium.webdriver.support.ui import Select
        Select(element).select_by_visible_text(value)

    elif input_type == "labelclick":
        # Find label with the correct text and click it
        labels = driver.find_elements(By.CSS_SELECTOR, selector)
        for label in labels:
            if label.text.strip().lower() == value.strip().lower():
                label.click()
                break
        else:
            raise ValueError(f"Label with text '{value}' not found at selector '{selector}'")

    else:
        raise NotImplementedError(f"Unsupported input type: {input_type}")


def uploadSecondaryImage(driver, prep_file):
    path = prep_file["path"]
    upload_selector = prep_file["upload"]["selector"]

    upload_elem = driver.find_element(By.CSS_SELECTOR, upload_selector)
    fileUpl(driver, path, upload_elem)

    if "caption" in prep_file:
        caption = prep_file["caption"]
        imageDesc(driver, caption, caption["value"])


FIELD_HANDLERS = {
    "text": textFill,
    "dropdown": dropChoose,
    "clickRadio": clickRadio,
    "checkboxMulti": clickMulti,
    "multi-text": multiWordFill,
    "button": clickButton,
}



def upload_content():
    platform_name = input("Enter the platform name (e.g., Art-Majeur, Saatchi-Art): ").strip().lower()
    catalog = load_catalog(platform_name)
    fieldset = load_fieldset(platform_name)
    driver = setUp(platform_name, catalog)
    content_id = get_content_by_id(catalog, content_id)

    try:
        content_id = int(input("Enter the ID of the content to upload: "))
        upload_content(driver, content_id, catalog, fieldset)
        print(f"✅ Successfully uploaded content ID {content_id}")
    except ValueError:
        print("❌ Invalid input. Please enter a numeric ID.")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

    


    return True


def main(): 
    upload_content()


if __name__ == "__main__":
    main()


