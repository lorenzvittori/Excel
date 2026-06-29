import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from pathlib import Path


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


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

BASE_DIR = Path(__file__).resolve().parent
SERVICE_ACCOUNT_FILE = BASE_DIR / "google_service_account.json"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

root_dir = BASE_DIR / "Dati" / "TabelleProcessed"

if __name__ == "__main__":
    sync_month_local(
        client,
        "2026",
        "06",
        str(root_dir)
    )