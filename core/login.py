import time
from core import loadFieldset
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def isLoggedIn(driver, fieldset):
    log_test = fieldset.get("log_test")
    try: 
        driver.find_element(By.CSS_SELECTOR, log_test)
        print("✅ Login successful.")
        return True
    except NoSuchElementException:
        print("❌ Login may have failed or needs manual intervention.")
        return False


def logIn(driver, secrets, fieldset, timeout=15):
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


    isLoggedIn(driver, fieldset, timeout=15)



