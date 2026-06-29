import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox import DropboxOAuth2FlowNoRedirect
from pathlib import Path
import json
import os


def get_dropbox_client() -> dropbox.Dropbox:
    print("APP_KEY presente:", APP_KEY is not None)
    print("APP_SECRET presente:", APP_SECRET is not None)
    print("REFRESH_TOKEN presente:", REFRESH_TOKEN is not None)
    APP_KEY = os.environ.get("DROPBOX_APP_KEY")
    APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
    REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

    # Fallback locale: legge da file
    if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
        CREDENTIALS_PATH = Path(__file__).resolve().parent / "dropbox_credentials.json"
        TOKEN_PATH = Path(__file__).resolve().parent / "token_dropbox.json"

        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(f"File credenziali non trovato: {CREDENTIALS_PATH}")
        if not TOKEN_PATH.exists():
            raise FileNotFoundError(f"File token non trovato: {TOKEN_PATH}")

        creds = json.loads(CREDENTIALS_PATH.read_text())
        token_data = json.loads(TOKEN_PATH.read_text())

        APP_KEY = creds["app_key"]
        APP_SECRET = creds["app_secret"]
        REFRESH_TOKEN = token_data["refresh_token"]

    try:
        dbx = dropbox.Dropbox(
            oauth2_refresh_token=REFRESH_TOKEN,
            app_key=APP_KEY,
            app_secret=APP_SECRET,
        )
        dbx.users_get_current_account()
        return dbx
    except AuthError:
        raise ValueError("Credenziali Dropbox non valide.")


def download_file_from_dropbox(download_folder: Path, file_name: str, blocca_se_esistente: bool = True):
    DROPBOX_FOLDER = "/TabelleApp"

    dbx = get_dropbox_client()

    # ---- DIRECTORY -----
    OUTPUT_DIR = download_folder / file_name
    DROPBOX_DIR = f"{DROPBOX_FOLDER}/{file_name}"

    # ---- CHECK DROPBOX -----
    try:
        dbx.files_get_metadata(DROPBOX_DIR)
    except ApiError:
        print(f"-!- File non trovato su Dropbox: {DROPBOX_DIR}")
        print("File disponibili nella cartella remota:")
        for f in dbx.files_list_folder(DROPBOX_FOLDER).entries:
            print(f"  - {f.name}")
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- CHECK LOCALE -----
    if not download_folder.exists():
        raise FileNotFoundError(f"Cartella di destinazione non esistente: {download_folder}")

    if OUTPUT_DIR.exists():
        if blocca_se_esistente:
            print(f"-!- File già esistente -> Download interrotto: {OUTPUT_DIR}")
            return
        else:
            print(f"-!- File già esistente -> Verrà sovrascritto: {OUTPUT_DIR}")

    # ---- DOWNLOAD -----
    dbx.files_download_to_file(str(OUTPUT_DIR), DROPBOX_DIR)
    print(f"Download completato: {OUTPUT_DIR}")


if __name__ == "__main__":
    download_file_from_dropbox(
        Path("C:/Users/lvitt/OneDrive/Documenti/GiuHub Local Repository/FLUSSO_SpeseEntrate/Dati/TabelleApp"),
        "app_2026_06.xlsx",
        blocca_se_esistente=True
    )