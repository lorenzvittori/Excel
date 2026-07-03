## NOME FILE: write_module.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import configuration as config
import os
from pathlib import Path


def get_google_client(google_service_account: Path) -> gspread.Client:
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
        if not google_service_account.exists():
            raise FileNotFoundError(f"File service account non trovato: {google_service_account}")
        creds = Credentials.from_service_account_file(google_service_account, scopes=SCOPES)

    return gspread.authorize(creds)


def sync_month_local(
        client: gspread.Client,
        anno: str,
        mese_str: str,
        df_prc: dict[str, pd.DataFrame],
        flag_sovrascrivi_celle: bool = False):

    # 1. GOOGLE SHEET
    sheet_name = config.MESI[mese_str]["nome_foglio_associato"]
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

    # 2. CHECK CELLE
    check = ws.get("B2:D2")
    row = check[0] if check else ["", "", ""]

    if any(str(cell).strip() != "" for cell in row):
        if not flag_sovrascrivi_celle:
            raise RuntimeError(f"[ERROR] \t Foglio non vuoto: {sheet_name}")
        else:
            print(f"[INFO] \t Foglio non vuoto - > SOVRASCRIVO CELLE")

    # 3. WRITE
    NOME_FOGLIO_SPESE   = config.DESIGN["NOME_FOGLIO_SPESE"]
    NOME_FOGLIO_ENTRATE = config.DESIGN["NOME_FOGLIO_ENTRATE"]
    df_spese_raw = pd.DataFrame(df_prc[NOME_FOGLIO_SPESE])
    #df_entrate_raw = pd.DataFrame(df_prc[NOME_FOGLIO_ENTRATE])
    
    # 3.1 WRITE SPESA
    ws = sheet.worksheet(NOME_FOGLIO_SPESE)
    ws.update(
        [df_spese_raw.columns.tolist()] + df_spese_raw.values.tolist(),
        "B1"
    )

