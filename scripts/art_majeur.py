from core import *

def runUpload(driver, fieldset, content, secrets):
    
    env = coreTestEnv(driver, fieldset, content, secrets)

    manTester(env)


if __name__ == "__main__":
    raise RuntimeError("This script is not meant to be run directly. Use main.py.")