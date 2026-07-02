## NOME FILE: write_module.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import configuration as config
import os


def get_google_client(struttura_repo: dict) -> gspread.Client:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT")

    if service_account_json:
        # GitHub Actions: legge dalla variabile d'ambiente
        service_account_info = json.loads(service_account_json)
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    else:
        # Fallback locale: legge da file
        SERVICE_ACCOUNT_FILE = struttura_repo["FILE_GOOGLE_ACCOUNT"]
        if not SERVICE_ACCOUNT_FILE.exists():
            raise FileNotFoundError(f"File service account non trovato: {SERVICE_ACCOUNT_FILE}")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    return gspread.authorize(creds)


def sync_month_local(
        client: gspread.Client,
        anno: str,
        struttura_repo: dict,
        mese_str: str,
        flag_sovrascrivi_celle: bool = False):

    file_name = config.get_processed_name(anno=anno, mese_str=mese_str)
    file_path = struttura_repo["FOLD_PRC_TBT"] / file_name

    sheet_name = config.MESI[mese_str]["nome_foglio_associato"]

    # 1. FILE LOCALE
    if not file_path.exists():
        raise FileNotFoundError(f"[ERROR] \t File locale mancante: {file_path}")

    df = pd.read_excel(file_path, sheet_name="Spese")
    df = df.fillna("")

    # 2. GOOGLE SHEET
    id_google_sheet = config.ID_GOOGLE_SHEET[anno]

    try:
        sheet = client.open_by_key(id_google_sheet)
    except gspread.exceptions.SpreadsheetNotFound:
        raise FileNotFoundError(f"[ERROR] \t Google Sheet non trovato: {id_google_sheet}")
    except gspread.exceptions.APIError as e:
        raise RuntimeError(f"[ERROR] \t API Google Sheets: {e}")

    try:
        ws = sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        raise FileNotFoundError(f"[ERROR] \t Worksheet non trovato: {sheet_name}")

    # 3. CHECK CELLE
    check = ws.get("B2:D2")
    row = check[0] if check else ["", "", ""]

    if any(str(cell).strip() != "" for cell in row):
        if not flag_sovrascrivi_celle:
            raise RuntimeError(f"[ERROR] \t Foglio non vuoto: {sheet_name}")
        else:
            print(f"[INFO] \t Foglio non vuoto - > SOVRASCRIVO CELLE")

    # 4. WRITE
    ws.update(
        [df.columns.tolist()] + df.values.tolist(),
        "B1"
    )

