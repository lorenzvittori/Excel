import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from pathlib import Path
import json
import os


def get_google_client():
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
        SERVICE_ACCOUNT_FILE = Path(__file__).resolve().parent / "google_service_account.json"
        if not SERVICE_ACCOUNT_FILE.exists():
            raise FileNotFoundError(f"File service account non trovato: {SERVICE_ACCOUNT_FILE}")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    return gspread.authorize(creds)


def sync_month_local(client, anno: str, mese: str, base_path: str):
    file_name = f"p_{anno}_{mese}.xlsx"
    file_path = Path(base_path) / file_name

    sheet_name = mese

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
    sheet = client.open_by_key("18E_u3WGZUrUJIcHfoC9ylt_uJiE3XxJ7XQyQkJC85kI")
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

    print(f"SYNC COMPLETATO {anno}-{mese}")


if __name__ == "__main__":
    client = get_google_client()
    root_dir = Path(__file__).resolve().parent / "Dati" / "TabelleProcessed"

    sync_month_local(
        client,
        "2026",
        "06",
        str(root_dir)
    )