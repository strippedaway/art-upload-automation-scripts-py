import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def goToUploadForm(driver, fieldset, timeout=15):
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