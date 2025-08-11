import time

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def prepElem(driver, fieldset, content, fieldName, timeout=10):
    field_conf = fieldset["fieldset"].get(fieldName)
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

FIELD_HANDLERS = {
    "text": textFill,
    "dropdown": dropChoose,
    "clickRadio": clickRadio,
    "checkboxMulti": clickMulti,
    "multi-text": multiWordFill,
    "button": clickButton,
}
