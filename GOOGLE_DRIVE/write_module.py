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
        anno: str, 
        mese_str: str, 
        struttura_repo: dict):
    
    file_name = config.get_processed_name(anno=anno, mese_str=mese_str)
    file_path = struttura_repo["FOLD_PRC_TBT"] / file_name

    sheet_name = config.MESI[mese_str]["nome_foglio_associato"]

    # -------------------------
    # 1. CHECK FILE LOCALE
    # -------------------------
    try:
        df = pd.read_excel(file_path, sheet_name="Spese")
    except FileNotFoundError:
        print(f"ERRORE: file non trovato -> {file_path}")
        raise SystemExit
    except Exception as e:
        print(f"ERRORE lettura Excel: {e}")
        raise SystemExit

    # -------------------------
    # 2. OPEN GOOGLE SHEET
    # -------------------------
    client = get_google_client(struttura_repo)
    id_google_sheet = config.ID_GOOGLE_SHEET[anno]
    
    sheet = client.open_by_key(id_google_sheet)
    ws = sheet.worksheet(sheet_name)

    # -------------------------
    # 3. CHECK CELLE B2:D2
    # -------------------------
    check = ws.get("B2:D2")[0]

    if any(str(cell).strip() != "" for cell in check):
        print("ERRORE: B2:D2 non vuote, stop esecuzione")
        raise SystemExit

    # -------------------------
    # 4. WRITE DATA
    # -------------------------
    df = df.fillna("")

    ws.update(
        [df.columns.tolist()] + df.values.tolist(),
        "B1"
    )

    print(f"SYNC COMPLETATO {anno}-{mese_str}")

