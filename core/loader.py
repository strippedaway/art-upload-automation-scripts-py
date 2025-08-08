import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")


def loadFFprofile(path="ff-profile.json"):
    filepath = os.path.join(DATA_DIR, path)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    ffprofile = data.get("ffprofile")
    if not ffprofile:
        raise ValueError("Firefox profile path not found in ff-profile.json")

    return ffprofile


def loadSecrets(platform_name, path="secrets.json"):
    filepath = os.path.join(DATA_DIR, path)
    with open(filepath, "r", encoding="utf-8") as f:
        all_secrets = json.load(f)

    for entry in all_secrets:
        if entry.get("platform", "").lower() == platform_name.lower():
            return entry

    raise ValueError(f"No credentials found for platform: {platform_name}")


def loadCatalog(platform_name):
    filename = f"{platform_name.lower()}-catalog.json"
    filepath = os.path.join(DATA_DIR, "catalogs", filename)
    with open(os.path.join(filepath), "r", encoding="utf-8") as f:
        return json.load(f)


def loadFieldset(platform_name):
    filename = f"{platform_name.lower()}-fieldset.json"
    filepath = os.path.join(DATA_DIR, "fieldsets", filename)
    with open(os.path.join(filepath), "r", encoding="utf-8") as f:
        return json.load(f)


def loadAll(platform_name):
    return {
        "secrets": loadSecrets(platform_name),
        "catalog": loadCatalog(platform_name),
        "fieldset": loadFieldset(platform_name)
        }