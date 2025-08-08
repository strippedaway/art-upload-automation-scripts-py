import importlib
import os

def loadPlatformScript(platform_name):
    script_path = os.path.join("scripts", f"{platform_name}-script.py")

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"No script found for platform: {platform_name}")

    spec = importlib.util.spec_from_file_location("platform_script", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.runUpload

def fetchContent(catalog, target_id):
    for cnt in catalog.get("content", []):
        if cnt.get("id") == target_id:
            return cnt
    raise ValueError(f"No content found with id {target_id}")