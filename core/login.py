import time
from core import loadFieldset
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


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
    safeGet(driver, secrets["address"])

    driver.get(secrets["address"])
    time.sleep(1)
    wait = WebDriverWait(driver, timeout)
    time.sleep(1.5)

    
    # Wait for email input
    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, secrets["email"]["field"])))
    time.sleep(2)
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

    if botCheckHard(driver):
        pauseForBot(driver, "bot check after submit")


    isLoggedIn(driver, fieldset)


def botCheckHard(driver):
    #cloudlfare bot pause
    print("🔍 Checking for bot-detection...")

    patterns = [
        # Common Cloudflare / bot protection selectors
        (By.CSS_SELECTOR, "script[src='https://static.cloudflareinsights.com']"),
        (By.CSS_SELECTOR, "a[href='https://www.cloudflare.com/*']"),
        (By.CLASS_NAME, "cf-browser-verification"),
        (By.XPATH, "//h1[contains(text(), 'Checking your browser')]"),
        (By.XPATH, "//h1[contains(text(), 'Verify you are human')]"),
        (By.XPATH, "//div[contains(text(), 'Enable JavaScript')]"),
        (By.XPATH, "//iframe[contains(@src, 'captcha')]"),
    ]

    found = False
    for by, selector in patterns:
        try:
            elem = driver.find_element(by, selector)
            if elem:
                found = True
                print(f"⚠️ Bot check detected via {by}={selector}")
                break
        except NoSuchElementException:
            continue

    if found:
        print("⏸️ Execution paused — solve the bot check manually in the browser.")
        print("   Once you have completed it, press Enter here to resume...")
        try:
            input()
        except KeyboardInterrupt:
            print("❌ Aborted by user.")
            driver.quit()
            exit(1)
        return True

    print("✅ No bot check detected.")
    return False

def pauseForBot(driver, reason="Bot/anti-automation suspected."):
    print(f"⏸️  {reason}")
    print("Solve whatever is on the page (captcha / Cloudflare / login),")
    print("then press Enter here to resume...")
    try:
        input()
    except KeyboardInterrupt:
        print("Aborted by user.")
        try:
            driver.quit()
        finally:
            raise SystemExit(1)


def safeGet(driver, url, wait_seconds=20):
    driver.get(url)
    # immediate hard-check
    if botCheckHard(driver):
        pauseForBot(driver, "Cloudflare/anti-bot screen detected after navigation.")
    return driver

def wait_clickable_or_pause(driver, by, sel, wait_seconds=20, reason="Expected element not clickable"):
    try:
        elem = WebDriverWait(driver, wait_seconds).until(
            EC.element_to_be_clickable((by, sel))
        )
        return elem
    except TimeoutException:
        # Secondary check: maybe it was a bot wall
        if botCheckHard(driver):
            pauseForBot(driver, f"{reason} — likely bot wall. Manual solve needed.")
            # Try once more after resume:
            return WebDriverWait(driver, wait_seconds).until(
                EC.element_to_be_clickable((by, sel))
            )
        # If still not bot, bubble up
        raise


def wait_visible_or_pause(driver, by, sel, wait_seconds=20, reason="Element not visible"):
    try:
        return WebDriverWait(driver, wait_seconds).until(
            EC.visibility_of_element_located((by, sel))
        )
    except TimeoutException:
        if botCheckHard(driver):
            pauseForBot(driver, f"{reason} — likely bot wall. Manual solve needed.")
            return WebDriverWait(driver, wait_seconds).until(
                EC.visibility_of_element_located((by, sel))
            )
        raise
