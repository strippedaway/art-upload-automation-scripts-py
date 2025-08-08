
from core import *


def main():
    platform_name, driver, catalog, fieldset = preparePlatform()
    while True:
        try:
            content_id = getContentID()
            content = fetchContent(catalog, content_id)
            secrets = loadSecrets(platform_name)
            runUpload = loadPlatformScript(platform_name)
            runUpload(driver, fieldset, content, secrets)

            print(f"✅ Successfully uploaded content ID {content_id}")
        except ValueError:
            print("❌ Please enter a numeric ID.")
        except Exception as e:
            print(f"❌ Upload failed: {e}")

        again = input("🔁 Upload another? (y/n): ").strip().lower()
        if again != 'y':
            driver.quit()
            break


if __name__ == "__main__":
    main()