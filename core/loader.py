import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def loadFFprofile(path="ff-profile.json"):
    filepath = os.path.join(BASE_DIR, "data", path)
    with open(os.path.join(filepath), "r", encoding="utf-8") as f:
        data = json.load(f)

    ffprofile = data.get("ffprofile")
    if not ffprofile:
        raise ValueError("Firefox profile path not found in ff-profile.json")

    return ffprofile

def loadSecrets(platform_name, path="secrets.json"):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), "r", encoding="utf-8") as f:
        all_secrets = json.load(f)

    for entry in all_secrets:
        if entry.get("platform", "Saatchi-Art").lower() == platform_name.lower():
            return entry

    raise ValueError(f"No credentials found for platform: {platform_name}")


def loadCatalog(platform_name):
    filename = f"{platform_name.lower()}-catalog.json"
    path = os.path.join(BASE_DIR, "data", "catalog", filename)
    with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def loadFieldset(platform_name):
    filename = f"{platform_name.lower()}-fieldset.json"
    path = os.path.join(BASE_DIR, "data", "fieldset", filename)
    with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
        return json.load(f)

def loadAll(platform_name):
    return {
        "secrets": loadSecrets(platform_name),
        "catalog": loadCatalog(platform_name),
        "fieldset": loadFieldset(platform_name)
        }