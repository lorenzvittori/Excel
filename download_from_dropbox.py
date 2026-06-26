import dropbox
from pathlib import Path

from MAIN import FILEAPP_FOLDER

#Constanti
TOKEN_FILE = "token_dropbox.txt"
MAIN_FOLDER = "Dati"
FILE_APP_FOLDER = "TabelleApp"

FILE_NAME = "app_2026_06.xlsx"


BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE_DIR = BASE_DIR / TOKEN_FILE


# Token
TOKEN = TOKEN_FILE_DIR.read_text().strip()
dbx = dropbox.Dropbox(TOKEN)


# file target
DROPBOX_PATH = f"/{FILE_APP_FOLDER}/{FILE_NAME}"
LOCAL_PATH = BASE_DIR / MAIN_FOLDER / FILE_APP_FOLDER / FILE_NAME

# download
dbx.files_download_to_file(str(LOCAL_PATH), DROPBOX_PATH)

print("Download completato:", LOCAL_PATH)