## NOME FILE: dropbox_module.py
import dropbox
from dropbox.exceptions import ApiError, AuthError
import configuration as config
import json
import os


def get_dropbox_client(struttura_repo: dict) -> dropbox.Dropbox:
    APP_KEY = os.environ.get("DROPBOX_APP_KEY")
    APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
    REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

    # Fallback locale: legge da file
    if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
        DROPBOX_CRED    = struttura_repo["FILE_DROPBOX_CRED"]
        DROPBOX_TOKEN   = struttura_repo["FILE_DROPBOX_TOKEN"]

        if not DROPBOX_CRED.exists():
            raise FileNotFoundError(f"File credenziali non trovato: {DROPBOX_CRED}")
        if not DROPBOX_TOKEN.exists():
            raise FileNotFoundError(f"File token non trovato: {DROPBOX_TOKEN}")

        creds = json.loads(DROPBOX_CRED.read_text())
        token_data = json.loads(DROPBOX_TOKEN.read_text())

        APP_KEY     = creds["app_key"]
        APP_SECRET  = creds["app_secret"]
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


def download_file_from_dropbox(
        dbx: dropbox.Dropbox,
        anno: str,
        mese_str: str,
        struttura_repo: dict,
        struttura_dbox: dict,
        blocca_se_esistente: bool = True):
    

    # ---- DIRECTORY -----
    DROPBOX_FOLDER = struttura_dbox["FOLD_RAW_TBT"]
    file_name = config.get_raw_name(anno = anno, mese_str = mese_str)
    DOWNLOAD_FOLDER = struttura_repo["FOLD_RAW_TBT"]
    OUTPUT_DIR  = DOWNLOAD_FOLDER / file_name
    DROPBOX_DIR = f"{DROPBOX_FOLDER}/{file_name}"

    # ---- CHECK DROPBOX -----
    try:
        dbx.files_get_metadata(DROPBOX_DIR)
    except ApiError:
        print(f"-!- File non trovato su Dropbox: {DROPBOX_DIR}")
        print("File disponibili nella cartella remota:")
        for f in dbx.files_list_folder(DROPBOX_FOLDER).entries: # type: ignore
            print(f"  - {f.name}")
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- CHECK LOCALE -----
    if not DOWNLOAD_FOLDER.exists():
        raise FileNotFoundError(f"Cartella di destinazione non esistente: {DOWNLOAD_FOLDER}")

    if OUTPUT_DIR.exists():
        if blocca_se_esistente:
            print(f"-!- File gia' esistente -> Download interrotto: {OUTPUT_DIR}")
            return
        else:
            print(f"-!- File gia' esistente -> Verra' sovrascritto: {OUTPUT_DIR}")

    # ---- DOWNLOAD -----
    dbx.files_download_to_file(str(OUTPUT_DIR), DROPBOX_DIR)
    print(f"Download completato: {OUTPUT_DIR}")
    
        
    print("File creato in:", OUTPUT_DIR)
    print("Esiste davvero:", OUTPUT_DIR.exists())


