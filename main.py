from core import *


def main():
    platform_name, driver, catalog, fieldset = preparePlatform()
    while True:
        try:
            content_id = getContentID()
            print("[main] getting contentID")

            content = fetchContent(catalog, content_id)
            print("[main] fetched content")

            secrets = loadSecrets(platform_name)
            print("[main] loaded secrets")

            runUpload = loadPlatformScript(platform_name)
            print(f"[main] got runUpload={runUpload}")

            runUpload(driver, fieldset, content, secrets)
            print("[main] returned from runUpload")


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


