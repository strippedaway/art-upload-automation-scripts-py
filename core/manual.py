import inspect
from core import (
    textFill, dropChoose, clickRadio, clickMulti, clickButton,
    prepFiles, fileUpl, uploadMainFile, uploadSecondaryFile,
    goToUploadForm, setUp, getContentID, getPlatform, preparePlatform,
)


def userPause(note: str = "Paused. Press Enter to continue..."):
    input(f"⏸️  {note}")


def manTester(env: dict):
    """
    Interactive tester for dynamically calling functions by name with arguments.
    `env` should contain all objects and functions you want available.
    """
    print("\n🧪 Manual Function Tester")
    print("Enter 'exit' at any prompt to cancel.")
    print(f"Available functions: {', '.join([k for k in env if callable(env[k])])}")
    print(f"Available objects:   {', '.join([k for k in env if not callable(env[k])])}")
    print()

    while True:
        fn_name = input("🔧 Function name to test: ").strip()
        if fn_name.lower() == "exit":
            break

        if fn_name not in env or not callable(env[fn_name]):
            print(f"❌ Function '{fn_name}' not found or not callable.")
            continue

        func = env[fn_name]
        sig = inspect.signature(func)
        print(f"📜 Function signature: {sig}")

        # Prompt for arguments
        raw_args = input("📥 Enter arguments (comma-separated): ").strip()
        if raw_args.lower() == "exit":
            break

        args = []
        for arg in raw_args.split(","):
            arg = arg.strip()

            # Look up variable from env or treat as literal
            if arg in env:
                args.append(env[arg])
            else:
                # Try to cast to int/float/bool if possible
                if arg.isdigit():
                    args.append(int(arg))
                elif arg.replace(".", "", 1).isdigit() and arg.count(".") < 2:
                    args.append(float(arg))
                elif arg.lower() in ("true", "false"):
                    args.append(arg.lower() == "true")
                else:
                    args.append(arg)

        try:
            result = func(*args)
            print(f"✅ Function returned: {result}\n")
        except Exception as e:
            print(f"❌ Error calling {fn_name}:\n{e}\n")

    print("🛑 Manual tester exited.\n")

def coreTestEnv(driver, fieldset, content=None, secrets=None):
    """
    Returns a dictionary of functions and objects for use in manTester().
    Can be extended with any runtime objects like `content`, `secrets`, etc.
    """
    env = {
        "driver": driver,
        "fieldset": fieldset,
        "userPause": userPause,

        # Upload field functions
        "textFill": textFill,
        "dropChoose": dropChoose,
        "clickRadio": clickRadio,
        "clickMulti": clickMulti,
        "clickButton": clickButton,

        # Upload file functions
        "prepFiles": prepFiles,
        "fileUpl": fileUpl,
        "uploadMainFile": uploadMainFile,
        "uploadSecondaryFile": uploadSecondaryFile,

        # Platform-related
        "goToUploadForm": goToUploadForm,
        "setUp": setUp,
        "getContentID": getContentID,
        "getPlatform": getPlatform,
        "preparePlatform": preparePlatform,
    }

    if content is not None:
        env["content"] = content
    if secrets is not None:
        env["secrets"] = secrets

    return env