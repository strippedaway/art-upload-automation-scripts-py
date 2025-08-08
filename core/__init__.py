#init file 
from .loader import loadFFprofile, loadSecrets, loadFieldset, loadCatalog, loadAll

from .driver import getDriver

from .login import logIn, isLoggedIn

from .autocomplete import textFill, dropChoose, clickRadio, clickMulti, clickButton

from .fileupload import prepFiles, fileUpl, uploadMainFile, uploadSecondaryFile

from .helpers import fetchContent, loadPlatformScript

from .uploader import goToUploadForm

from .setup import setUp, getContentID, getPlatform, preparePlatform