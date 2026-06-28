import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
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
    df = pd.read_excel(file_path, sheet_name="Spese")
    
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

TOKEN_FILE = "token.json"

creds = None

if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

# 👇 QUESTA È LA RIGA CHE TI MANCAVA
client = gspread.authorize(creds)

from pathlib import Path

root_dir = Path(__file__).resolve().parent / "Dati" / "TabelleProcessed"

sync_month_local(
    client,
    "2026",
    "06",
    str(root_dir)
)