from .loader import *
from .driver import *
from .login import *
from .helpers import *


def setUp(platform_name, headless=False):
    PROFILE_PATH = loadFFprofile()
    driver = getDriver(profile_path=PROFILE_PATH, headless=headless)
    
    secrets = loadSecrets(platform_name)
    fieldset = loadFieldset(platform_name)

    logIn(driver, secrets, fieldset, 10)

    return driver, fieldset 


def getPlatform():
    platform_name = input("Enter the platform name (e.g., Art-Majeur, Saatchi-Art): ").strip().lower()
    return platform_name


def getContentID():
    try:
        return int(input("Enter the ID of the content to upload: "))
    except ValueError:
        raise ValueError("Invalid ID")
    

def preparePlatform():
    platform_name = getPlatform()
    driver, fieldset = setUp(platform_name)
    catalog = loadCatalog(platform_name)
    return platform_name, driver, catalog, fieldset