import os
import time

from selenium.webdriver.common.by import By

def prepFiles(content, fieldset):
    base_path = content.get("file_directory", "")
    file_data = content.get("files", {})
    results = []

    # MAIN
    if "primary_file" in file_data and "primary_file" in fieldset:
        results.append({
            "is_main": True,
            "path": os.path.join(base_path, file_data["primary_file"]),
            "upload": fieldset["primary_file"]
        })

    # SECONDARY
    for key in sorted(file_data.keys()):
        if key.startswith("file") and key != "primary_file":
            try:
                index = int(key.replace("file", ""))
            except ValueError:
                continue

            file_path = os.path.join(base_path, file_data[key])
            upload_conf = fieldset.get("file")  # shared file selector
            if not upload_conf:
                continue  # no upload input defined

            entry = {
                "is_main": False,
                "path": file_path,
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


def fileUpl(driver, file_path, fieldName):
    try:
        fieldName.send_keys(file_path)
        print(f"✅ Uploaded file: {file_path}")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"❌ Failed to upload file '{file_path}': {e}")
        # manualIntervention(driver, f"Could not upload {file_path}. Please upload manually.")
        return False


def uploadMainFile(driver, file_data):
    for file in file_data:
        if file.get("is_main"):
            path = file["path"]
            selector = file["upload"]["selector"]

            element = driver.find_element(By.CSS_SELECTOR, selector)

            fileUpl(driver, path, selector)
            break


def fileDesc(driver, caption, value):

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


def uploadSecondaryFile(driver, prep_file):
    path = prep_file["path"]
    upload_selector = prep_file["upload"]["selector"]

    upload_elem = driver.find_element(By.CSS_SELECTOR, upload_selector)
    fileUpl(driver, path, upload_elem)

    if "caption" in prep_file:
        caption = prep_file["caption"]
        fileDesc(driver, caption, caption["value"])

