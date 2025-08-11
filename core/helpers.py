import os, sys, importlib.util, importlib.machinery, py_compile, inspect, time

class PlatformScriptError(Exception): ...
class PlatformScriptNotFound(PlatformScriptError): ...
class PlatformScriptLoadError(PlatformScriptError): ...
class PlatformScriptEntryMissing(PlatformScriptError): ...

def loadPlatformScript(platform_name: str, scripts_dir: str = "scripts"):
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)

    # 1) Normalize name and build path
    norm = str(platform_name).strip().lower().replace(" ", "_").replace("-", "_")
    filename = f"{norm}.py"
    script_path = os.path.abspath(os.path.join(scripts_dir, filename))

    print(f"[loader] platform={platform_name!r} norm={norm!r}")
    print(f"[loader] script_path={script_path}")

    # 2) Existence
    if not os.path.isfile(script_path):
        raise PlatformScriptNotFound(f"No script found for platform '{platform_name}' at {script_path}")

    # 3) Syntax check early (better error than during exec)
    try:
        py_compile.compile(script_path, doraise=True)
    except py_compile.PyCompileError as e:
        raise PlatformScriptLoadError(f"Syntax error compiling {script_path}:\n{e}") from e

    # 4) Unique module name to avoid stale cache while iterating
    mod_name = f"platforms.{norm}_script_{int(os.path.getmtime(script_path))}_{int(time.time()*1000)}"
    spec = importlib.util.spec_from_file_location(mod_name, script_path)
    if spec is None or spec.loader is None:
        raise PlatformScriptLoadError(f"Could not create import spec for {script_path}")

    # Ensure a clean slate if name somehow collides
    sys.modules.pop(mod_name, None)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise PlatformScriptLoadError(f"Exception while importing {script_path}: {e}") from e

    # 5) Locate entry function
    entry_names = ("runUpload", "run_upload", "main", "run")
    entry = None
    for name in entry_names:
        if hasattr(module, name):
            entry = getattr(module, name)
            break
    if entry is None:
        raise PlatformScriptEntryMissing(
            f"{script_path} does not define any of {entry_names}"
        )
    if not callable(entry):
        raise PlatformScriptEntryMissing(
            f"{script_path} attribute '{entry.__name__}' is not callable"
        )

    # 6) Optional: sanity-check signature (non-fatal; warn only)
    try:
        sig = inspect.signature(entry)
        print(f"[loader] entry={entry.__name__}{sig}")
    except Exception:
        pass

    print(f"[loader] Loaded {entry.__name__} from {script_path}")
    return entry


def fetchContent(catalog, target_id):
    items = catalog.get("content", [])
    tid = str(target_id).strip()

    for cnt in items:
        if cnt in items:
            return cnt
    
    print(f"[fetchContent] id= {tid} not found. ")
    return None