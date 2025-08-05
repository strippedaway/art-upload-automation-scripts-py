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
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="imageFile"]'))  # or any upload form field
        )
        print("[go_to_upload_form] Upload form is ready.")
    except Exception as e:
        print(f"[go_to_upload_form] Failed to load upload form: {e}")


def is_logged_in(driver):
    try: 
        driver.find_element(By.CSS_SELECTOR, 'a[href="/en/logout"]')
        return True
    except NoSuchElementException:
        return False


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
    try:
        main_image_path = os.path.abspath(os.path.join(art["image_directory"],art["images"]["primary_image"]))
        time.sleep(1)

        file_input = driver.find_element(By.CSS_SELECTOR, '#fileuploader_container input[name="imageFile"]')
        file_input.send_keys(main_image_path)
        
        print("Main image upload initiated.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/image/additional/new/file"]'))
        )
        print("Upload of of main.jpg complete")

    except Exception as e:
        print(f"[uploadMain] Error uploading main image: {e}")


def imageUpload(driver, art):
    images = art.get("images, {}")
    
    additional_keys = sorted(k for k in images if k.startswith("image") and k != "primary_image")

    for image_key in additional_keys:
        caption_key = "caption" + image_key.replace("image", "")
        image_file = os.path.abspath(os.path.join(art["image_directory"], images[image_key]))
        caption_text = images.get(caption_key, "")

        print(f"Uploading {image_key} with caption: {caption_text}")

        try:
            add_photo_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/image/additional/new/file"]'))
            )
            add_photo_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="form[type]"]'))  
            )

            select_element = Select(driver.find_element(By.CSS_SELECTOR, 'select[name="form[type]"]'))
            select_element.select_by_visible_text(caption_text)

            file_input = driver.find_element(By.CSS_SELECTOR, 'input[name="imageFile"]')
            file_input.send_keys(image_file)

            WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/image/additional/new/file"]'))
            )

            print("[imageUpload] All additional images uploaded.")

        except Exception as e:
            print(f"[imageupload] Failed to upload {image_key}: {e}")


def autoComplete(driver, art):
    #navigate to detail editing page
    try:
        current_url  = driver.current_url

        match = re.search(r'/artworks/(\d+)/', current_url)
        if not match:
            print("[autoComplete] Could not extract artwork ID from URL.")
            return
        
        artwork_id = match.group(1)
        print(f"[autoComplete] Artowrk ID: {artwork_id}")

        edit_url = f"https://www.artmajeur.com/en/account/karen-terzyan/artworks/{artwork_id}/edit"
        driver.get(edit_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'form'))
        )
        
        print(f"[autoComplete] Reached edit page for artwork {artwork_id}.")
   
    except Exception as e:
        print(f"[autoComplete] Error: {e}")
        return

    #add first INFO fieldset info .
    try: 
        title_input =  WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "artwork_rawTitle"))
        )

        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", title_input)
        time.sleep(0.5)

        title_input.clear()
        title_input.send_keys(art["title"])
        time.sleept(0.4)

        year_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "artwork_year"))
        )
        year_input.clear()
        year_input.send_keys(str(art["year"]))
        time.sleep(0.4)


        print("[autoComplete] Section 1: Title and Year completed.")

    except Exception as e:
        print(f"[autoComplete] Error in Info section: {e}")

    #family filter
    try:
        family_safe = art.get("family_filter", "").strip().lower() == "yes"
        radio_id = "artwork_isFamilySafe_0" if family_safe else "artwork_isFamilySafe_1"

        radio_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, radio_id))
        )

        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", radio_input)
        time.sleep(0.3)
        radio_input.click()
        time.sleep(0.4)

        print(f"[autoComplete] Family filter set to {'yes' if family_safe else 'no'}.")

    except Exception as e:
        print(f"[autoComplete] Error setting Family Filter: {e}")

    
    # Categorization: 

    try:
        category_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "artwork_category"))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", category_dropdown)
        time.sleep(0.4)

        select = Select(category_dropdown)
        select.select_by_visible_text(art["primary_type"])
        time.sleep(0.5)

        print(f"[autoComplete] Category set to: {art['primary_type']}")

    except Exception as e:
        print(f"[autoComplete] Error setting category: {e}")

    #classifications:

    
    def click_matching_techniques(container_id, techniques):
        try:
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, container_id))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", container)
            time.sleep(0.5)

            labels = container.find_elements(By.TAG_NAME, "label")

            for label in labels:
                text = label.text.strip()
                if text in techniques:
                    try:
                        label.click()
                        print(f"[autoComplete] Technique selected: {text}")
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"[autoComplete] Could not click label: {text} – {e}")

        except Exception as e:
            print(f"[autoComplete] Error in technique section '{container_id}': {e}")

    click_matching_techniques("technics_container_paidra", art.get("paint_draw_techniques", []))
    click_matching_techniques("technics_container_scu", art.get("sculpture_techniques", []))

    #main, sig, unique

    try:
        main_tech = art.get("main_technique", "").strip()
        if main_tech:
            dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "artwork_mainTechnique"))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", dropdown)
            time.sleep(0.3)

            print(f"[autoComplete] Main technique set: {main_tech}")

    except Exception as e:
        print(f"[autoComplete] Error setting main technique: {e}")

    #support substrate

    try:
        support = art.get("support", "").strip()
        if support:
            support_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "artwork_substrate"))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", support_select)
            time.sleep(0.3)

            Select(support_select).select_by_visible_text(support)
            time.sleep(0.4)
            print(f"[autoComplete] Support/substrate set: {support}")
    except Exception as e:
        print(f"[autoComplete] Error setting support: {e}")

    #signature

    try:
        signature = art.get("signature", "").strip()
        if signature:
            signature_labels = driver.find_elements(By.CSS_SELECTOR, "#artwork_signatures label")
            for label in signature_labels:
                if label.text.strip() == signature:
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", label)
                    time.sleep(0.2)
                    label.click()
                    print(f"[autoComplete] Signature selected: {signature}")
                    time.sleep(0.3)
                    break
    except Exception as e:
        print(f"[autoComplete] Error setting signature: {e}")

    #art-type

    try:
        art_type = art.get("art_type", "").strip()
        if art_type:
            type_labels = driver.find_elements(By.CSS_SELECTOR, "#artwork_copyType label")
            for label in type_labels:
                if label.text.strip() == art_type:
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", label)
                    time.sleep(0.2)
                    label.click()
                    print(f"[autoComplete] Artwork type selected: {art_type}")
                    time.sleep(0.3)
                    break    
    except Exception as e:
        print(f"[autoComplete] Error setting artwork type: {e}")

    #presentation

    try:
        display_wall = art.get("display_wall", "").strip().lower()
        if display_wall:
            wall_labels = driver.find_elements(By.CSS_SELECTOR, "#artwork_isDisplayableOnWall label")
            for label in wall_labels:
                if label.text.strip().lower() == display_wall:
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", label)
                    time.sleep(0.2)
                    label.click()
                    time.sleep(0.3)
                    print(f"[autoComplete] Display on wall set to: {display_wall}")
                    break
    except Exception as e:
        print(f"[autoComplete] Error setting 'Display on wall': {e}")

    # --- PRESENTATION: Framing ---
    try:
        frame = art.get("frame", "").strip().lower()
        if frame:
            frame_labels = driver.find_elements(By.CSS_SELECTOR, "#artwork_isFramed label")
            for label in frame_labels:
                if label.text.strip().lower() == frame:
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", label)
                    time.sleep(0.2)
                    label.click()
                    time.sleep(0.3)
                    print(f"[autoComplete] Frame set to: {frame}")
                    break
    except Exception as e:
        print(f"[autoComplete] Error setting 'Frame': {e}")

    #dimensions and weight

    try:
        dimensions = art.get("dimensions", {})
        weight = art.get("weight", {})

        fieldset = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dimensions"))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", fieldset)
        time.sleep(0.4)

        # check n set unit
        unit = dimensions.get("unit", "").strip()
        if unit:
            unit_select = fieldset.find_element(By.ID, "artwork_lengthUnit")
            Select(unit_select).select_by_visible_text(unit)
            time.sleep(0.3)
            print(f"[autoComplete] Unit set to: {unit}")

        #inputting
        inputs = {
            "artwork[height]": dimensions.get("height"),
            "artwork[width]": dimensions.get("width"),
            "artwork[thickness]": dimensions.get("depth"),  # depth → thickness
            "artwork[weight]": weight.get("value")
        }

        for name, value in inputs.items():
            if value is not None:
                input_field = fieldset.find_element(By.NAME, name)
                input_field.clear()
                input_field.send_keys(str(value))
                time.sleep(0.3)
                print(f"[autoComplete] Set {name} = {value}")

    except Exception as e:
        print(f"[autoComplete] Error setting dimensions/weight: {e}")

    #sale
    try:
        sale_status = art.get("sale_status", "").strip()
        price = art.get("price", {}).get("value", None)
        packaging = art.get("packaging", "").strip()

        sale_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sale_section"))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", sale_section)
        time.sleep(0.4)

        # Set sale status (For Sale, Not For Sale, Sold, etc.)
        if sale_status:
            availability = sale_section.find_element(By.ID, "artwork_availability")
            Select(availability).select_by_visible_text(sale_status)
            time.sleep(0.3)
            print(f"[autoComplete] Sale status set to: {sale_status}")

        # Set price
        if price is not None:
            price_input = sale_section.find_element(By.NAME, "artwork[price]")
            price_input.clear()
            price_input.send_keys(str(price))
            time.sleep(0.3)
            print(f"[autoComplete] Price set to: {price}")

        # Set packaging
        if packaging:
            packaging_select = sale_section.find_element(By.NAME, "artwork[packagingType]")
            Select(packaging_select).select_by_visible_text(packaging)
            time.sleep(0.3)
            print(f"[autoComplete] Packaging set to: {packaging}")

    except Exception as e:
        print(f"[autoComplete] Error in sale section: {e}")


    #digital licensing
    try:
        if art.get("digital_print", "").strip():
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "artwork_isDigitalActivated"))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", checkbox)
            time.sleep(0.3)

            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(0.3)
                print("[autoComplete] Digital licensing enabled.")
            else:
                print("[autoComplete] Digital licensing already checked.")
    except Exception as e:
        print(f"[autoComplete] Error enabling digital licensing: {e}")

    #about artwork
    try:
        about_fields = {
            "condition": "artwork_quality",
            "style": "artwork_style",
            "theme": "artwork_theme",
        }

        for key, selector_id in about_fields.items():
            value = art.get(key, "").strip()
            if value:
                dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, selector_id))
                )
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", dropdown)
                Select(dropdown).select_by_visible_text(value)
                time.sleep(0.3)
                print(f"[autoComplete] Set {key}: {value}")

        # Descr
        description = art.get("description", "").strip()
        if description:
            description_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "artwork_description"))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", description_box)
            description_box.clear()
            description_box.send_keys(description)
            time.sleep(0.3)
            print("[autoComplete] Description filled.")

        # Internal SKU
        sku = art.get("internal-sku", "").strip()
        if sku:
            sku_input = driver.find_element(By.ID, "artwork_sku")
            sku_input.clear()
            sku_input.send_keys(sku)
            time.sleep(0.3)
            print(f"[autoComplete] Internal SKU set: {sku}")

        # Keywords (enter one by one with Enter key)
        from selenium.webdriver.common.keys import Keys

        keywords = art.get("keywords", [])
        if keywords:
            keyword_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "artwork_keywords"))
            )
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", keyword_input)
            for word in keywords:
                keyword_input.send_keys(word)
                time.sleep(0.1)
                keyword_input.send_keys(Keys.ENTER)
                time.sleep(0.2)
            print(f"[autoComplete] Keywords entered: {keywords}")

    except Exception as e:
        print(f"[autoComplete] Error in 'About this Artwork': {e}")


    #save button
    try:
        # Find the save button at the sticky footer
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"][aria-label="Save"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", save_button)
        time.sleep(0.4)
        
        save_button.click()
        print("[autoComplete] Save button clicked.")

        # Optional: wait for a flash message, redirect, or success confirmation
        time.sleep(2)  # crude delay — replace with specific wait if needed

        # Go back to upload page for next artwork
        go_to_upload_form(driver)

    except Exception as e:
        print(f"[autoComplete] Error during save/redirect: {e}")


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


