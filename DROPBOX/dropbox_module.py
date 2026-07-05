## NOME FILE: dropbox_module.py
from pathlib import Path
import dropbox
from dropbox.exceptions import ApiError, AuthError
import json
import os
import pandas as pd
import io


def get_dropbox_client(
        dropbox_credential: Path, 
        dropbox_token: Path) -> dropbox.Dropbox:
    APP_KEY = os.environ.get("DROPBOX_APP_KEY")
    APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")
    REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")

    # Fallback locale: legge da file
    if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
        DROPBOX_CRED    = dropbox_credential
        DROPBOX_TOKEN   = dropbox_token

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


def get_dataframe_from_dropbox(
        dbx: dropbox.Dropbox,
        dropbox_folder: str,
        file_name: str,
        sheet_name=None) -> dict[str, pd.DataFrame] | pd.DataFrame:

    DROPBOX_FOLDER = dropbox_folder
    DROPBOX_DIR = f"{DROPBOX_FOLDER}/{file_name}"

    # ---- CHECK DROPBOX -----
    try:
        dbx.files_get_metadata(DROPBOX_DIR)
    except ApiError:
        print(f"[ERROR] \t File non trovato su Dropbox: {DROPBOX_DIR}")
        print("[INFO] \t File disponibili nella cartella remota:")
        for f in dbx.files_list_folder(str(DROPBOX_FOLDER)).entries:  # type: ignore
            print(f"  - {f.name}")
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- DOWNLOAD IN MEMORIA -----
    _, response = dbx.files_download(DROPBOX_DIR)           # type: ignore
    print(f"[OK] \t File letto da Dropbox: {DROPBOX_DIR}")

    return pd.read_excel(io.BytesIO(response.content), header = None, sheet_name=sheet_name)


def download_file_from_dropbox(
        dbx: dropbox.Dropbox,
        dropbox_folder: str,
        file_name: str,
        local_folder: Path,
        blocca_se_esistente: bool = True):
    

    # ---- DIRECTORY -----
    DROPBOX_FOLDER = dropbox_folder
    DOWNLOAD_FOLDER = local_folder
    OUTPUT_DIR  = DOWNLOAD_FOLDER / file_name
    DROPBOX_DIR = f"{DROPBOX_FOLDER}/{file_name}"

    # ---- CHECK DROPBOX -----
    try:
        dbx.files_get_metadata(DROPBOX_DIR)
    except ApiError:
        print(f"[ERROR] \t File non trovato su Dropbox: {DROPBOX_DIR}")
        print("[INFO] \t File disponibili nella cartella remota:")
        for f in dbx.files_list_folder(DROPBOX_FOLDER).entries: # type: ignore
            print(f"  - {f.name}")
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- CHECK LOCALE -----
    if not DOWNLOAD_FOLDER.exists():
        print(f"[ERROR] \t Cartella di destinazione non esistente: {DOWNLOAD_FOLDER}")
        raise FileNotFoundError(f"Cartella di destinazione non esistente: {DOWNLOAD_FOLDER}")

    if OUTPUT_DIR.exists():
        if blocca_se_esistente:
            print(f"[ERROR] \t File gia' esistente -> Download interrotto: {OUTPUT_DIR}")
            return
        else:
            print(f"[WARNING] \t File gia' esistente -> sovrascritto: {OUTPUT_DIR}")

    # ---- DOWNLOAD -----
    dbx.files_download_to_file(str(OUTPUT_DIR), DROPBOX_DIR)
    print(f"[OK] \t Download completato: {OUTPUT_DIR}")    
    print(f"[INFO] \t File creato in: {OUTPUT_DIR}")


def upload_dataframe_to_dropbox(
        dbx: dropbox.Dropbox,
        dropbox_folder: str,
        file_name: str,
        df: pd.DataFrame | dict[str, pd.DataFrame],
        flag_sovrascrivi: bool = True):

    # ---- DATAFRAME -> BYTES IN MEMORIA -----
    buffer = io.BytesIO()
    
    if isinstance(df, dict):
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for sheet_name, sheet_df in df.items():
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        df.to_excel(buffer, index=False)
    
    # ---- UPLOAD -----
    DROPBOX_DIR = f"{dropbox_folder}/{file_name}"
    mode = dropbox.files.WriteMode.overwrite if flag_sovrascrivi else dropbox.files.WriteMode.add # type: ignore

    dbx.files_upload(buffer.getvalue(), DROPBOX_DIR, mode=mode)
    print(f"[OK] \t Upload completato: {DROPBOX_DIR}")