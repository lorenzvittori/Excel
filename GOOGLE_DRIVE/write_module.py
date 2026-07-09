## NOME FILE: write_module.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import configuration as config
import os
from pathlib import Path
import logger



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


def sync_entrate_totali(
        client: gspread.Client,
        anno: str,
        mese_str: str,
        df_entrate_prc: pd.DataFrame) -> None:

    id_google_sheet = config.ID_GOOGLE_SHEET[anno]
    NOME_FOGLIO_TOTALE = config.DESIGN["NOME_FOGLIO_TOTAL_ENTRATE"]

    try:
        sheet = client.open_by_key(id_google_sheet)
    except gspread.exceptions.SpreadsheetNotFound:
        raise FileNotFoundError(f"Google Sheet non trovato: {id_google_sheet}")
    except gspread.exceptions.APIError as e:
        raise RuntimeError(f"API Google Sheets: {e}")

    try:
        ws = sheet.worksheet(NOME_FOGLIO_TOTALE)
    except gspread.exceptions.WorksheetNotFound:
        raise FileNotFoundError(f"Worksheet non trovato: {NOME_FOGLIO_TOTALE}")

    df_entrate_nuove = df_entrate_prc.copy()
    df_entrate_nuove = df_entrate_nuove.fillna("")

    # ---- 1. LEGGI LA TABELLA ESISTENTE ----
    valori_esistenti = ws.get_all_values()

    if valori_esistenti:
        header = valori_esistenti[0]
        righe = valori_esistenti[1:]
        df_esistente = pd.DataFrame(righe, columns=header)
    else:
        df_esistente = pd.DataFrame(columns=df_entrate_nuove.columns.tolist())

    df_esistente = df_esistente.fillna("")

    df_esistente["Importo"] = df_esistente["Importo"].apply(
        lambda x: x.replace("€", "").replace(".", "").strip() if pd.notnull(x) else ""
    )

    df_esistente["Data"] = pd.to_datetime(df_esistente["Data"], errors="coerce", dayfirst=True)
    df_entrate_nuove["Data"] = pd.to_datetime(df_entrate_nuove["Data"], errors="coerce", dayfirst=True)

    righe_esistenti_totale = len(df_esistente.index)

    # ---- 2. RIMUOVI LE RIGHE DELLO STESSO ANNO/MESE (evita duplicati su rilancio) ----
    if "Mese" in df_esistente.columns:
        righe_da_togliere = (df_esistente["Mese"].astype(str) == str(int(mese_str)))
        righe_rimosse = int(len(righe_da_togliere))
        maschera = ~righe_da_togliere                   #inverte i booleani
        df_esistente = df_esistente[maschera]             #filtra per mastera = True
    else:
        righe_rimosse = 0

    # ---- 3. UNISCI (nessuna deduplica per contenuto: righe identiche legittime restano entrambe) ----
    df_union = pd.concat([df_esistente, df_entrate_nuove], ignore_index=True)
    df_union = df_union.sort_values(by=["Data", "Importo", "Note"])

    df_union["Data"] = df_union["Data"].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
    )

    df_union.reset_index(drop=True, inplace=True)
    df_union = df_union.fillna("")

    righe_rimaste = len(df_union.index)

    logger.info_mex(
        f"'{NOME_FOGLIO_TOTALE}' aggiornato per ANNO {anno} - MESE {mese_str}",
        dettaglio=[
            f"Righe esistenti prima dell'update: {righe_esistenti_totale}",
            f"Righe rimosse (stesso ANNO/MESE, sostituite): {righe_rimosse}",
            f"Righe nuove aggiunte: {len(df_entrate_nuove)}",
            f"Righe totali finali: {righe_rimaste}"
        ]
    )

    # ---- 4. SCRIVI TUTTO A PARTIRE DA A1 ----
    ws.clear()
    ws.update(
        [df_union.columns.tolist()] + df_union.values.tolist(),
        "A1"
    )




def sync_spese_mensili(
        client: gspread.Client,
        anno: str,
        mese_str: str,
        df_spese_prc: pd.DataFrame,
        flag_sovrascrivi_celle: bool = False):

    # 1. GOOGLE SHEET
    NOME_SHEET_MESE = config.MESI[mese_str]["nome_foglio_associato"]
    id_google_sheet = config.ID_GOOGLE_SHEET[anno]

    try:
        sheet = client.open_by_key(id_google_sheet)
    except gspread.exceptions.SpreadsheetNotFound:
        raise FileNotFoundError(f"Google Sheet non trovato: {id_google_sheet}")
    except gspread.exceptions.APIError as e:
        raise RuntimeError(f"API Google Sheets: {e}")

    try:
        ws = sheet.worksheet(NOME_SHEET_MESE)
    except gspread.exceptions.WorksheetNotFound:
        raise FileNotFoundError(f"Worksheet non trovato: {NOME_SHEET_MESE}")
    

    # 2. CHECK
    # 2.1 CONTROLLO SE CI SONO VALORI PRESENTI SUL FOGLIO
    check = ws.get("B2:G2")
    row = check[0] if check else ["", "", "", "", "", ""]

    if any(str(cell).strip() != "" for cell in row):
        if not flag_sovrascrivi_celle:
            logger.error_mex(f"Foglio non vuoto: {NOME_SHEET_MESE}")
            raise SystemExit
        else:
            logger.info_mex("Foglio non vuoto -> SOVRASCRIVO CELLE")
            
    # 2.2 CONTROLLO CHE NON HO PIU DI 500 RIGHE DA SCRIVERE:
    count_rows = len(df_spese_prc.index)
    if count_rows > 500:
        logger.warning_mex("Stai scrivendo più di 500 righe")
        
    # 2.3 CONTROLLO CHE STO SCRIVENDO IL NUMERO GIUSTO DI COLONNE
    count_colums = len(df_spese_prc.columns)
    if count_colums > config.NUMERO_COLONNE_SHEET_SPESE:
        logger.error_mex(f"Stai scrivendo più di {config.NUMERO_COLONNE_SHEET_SPESE} colonne")
        raise ValueError
    
    
    # 3. WRITE
    # 3.1 ELIMINO TUTTI I VALORI DELLE CELLE A2:F550
    ws.batch_clear(["B2:G550"])
    logger.info_mex("Celle B2:G550 svuotate prima della scrittura")
    
    # 3.2 WRITE SPESA
    df_spese_prc_clean = df_spese_prc.fillna("")
    ws.update(
        [df_spese_prc_clean.columns.tolist()] + df_spese_prc_clean.values.tolist(),
        "B1"
    )