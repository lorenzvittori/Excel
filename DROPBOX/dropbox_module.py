## NOME FILE: dropbox_module.py
from pathlib import Path
import dropbox
from dropbox.exceptions import ApiError, AuthError
import json
import os
import pandas as pd
import io
import configuration as config
import logger


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
            logger.tipo_messaggio(
                    tipo = "ERROR",
                    corpo= "File credenziali DropBox non trovato:",
                    dettaglio=f"{DROPBOX_CRED}")
            raise FileNotFoundError
        if not DROPBOX_TOKEN.exists():
            logger.tipo_messaggio(
                    tipo = "ERROR",
                    corpo= "File token DropBox non trovato:",
                    dettaglio=f"{DROPBOX_TOKEN}")
            raise FileNotFoundError

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
        logger.tipo_messaggio(
            tipo = "ERROR",
            corpo= "Credenziali non valide")
        raise ValueError


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
    
    
def smista_file_excel(
        dbx: dropbox.Dropbox,
        dropbox_folder_origine: str,
        dropbox_folder_destinazione: str,
        get_raw_name,
        estesione_files: str = ".xlsx",
        target_broken_name: str = "BROKEN",
        nome_colonna_data: str = "Data e ora",
        righe_da_saltare: int = 1,
        flag_sovrascrivi_raw: bool = False #ciao
        ) -> dict[str, list[dict]]:
    """
    Scansiona tutti i file con estensione estesione_files presenti in
    dropbox_folder_origine.
    Per ciascun file:
    - elimina, prima di iniziare, tutti i file broken residui di run precedenti
        (qualsiasi file che inizia con target_broken_name)
    - legge il primo foglio dell'excel, saltando righe_da_saltare righe iniziali
        (es. una riga di titolo sopra la vera intestazione)
    - verifica che tutte le date nella colonna nome_colonna_data
        appartengano allo stesso anno e allo stesso mese
    - se conforme, rinomina il file usando get_raw_name(anno, mese_str)
        e lo sposta in dropbox_folder_destinazione
    - se non conforme (date miste, colonna assente, file illeggibile),
        lo rinomina con target_broken_name (con un progressivo se ce n'è più
        di uno nella stessa esecuzione) e lo lascia in dropbox_folder_origine
    """

    entries = dbx.files_list_folder(dropbox_folder_origine).entries  # type: ignore
    file_xlsx = [f for f in entries if f.name.lower().endswith(estesione_files.lower())]

    if not file_xlsx:
        print(f"[INFO] \t Nessun file .xlsx trovato in {dropbox_folder_origine}")
        return {"SMISTATI": [], "BROKEN": []}

    # ---- PULIZIA BROKEN RESIDUI DI RUN PRECEDENTI ----
    file_broken_residui = [
        f for f in file_xlsx
        if f.name.startswith(target_broken_name)
    ]
    for f in file_broken_residui:
        dbx.files_delete_v2(f"{dropbox_folder_origine}/{f.name}")
        print(f"[INFO] \t Rimosso broken residuo: {f.name}")

    # ---- LISTA FILE DA PROCESSARE (escludo i broken residui appena eliminati) ----
    file_xlsx = [f for f in file_xlsx if f.name not in {f.name for f in file_broken_residui}]

    file_smistati = {
        "SMISTATI": [],
        "BROKEN": []
    }
    contatore_broken = 0

    for file_entry in file_xlsx:
        file_name = file_entry.name
        dropbox_path = f"{dropbox_folder_origine}/{file_name}"

        print(f"\n[INFO] \t Controllo file: {file_name}")

        # ---- DOWNLOAD ----
        try:
            _, response = dbx.files_download(dropbox_path)  # type: ignore
        except ApiError as e:
            print(f"[ERROR] \t Impossibile scaricare {file_name}: {e}")
            continue

        # ---- LETTURA PRIMO FOGLIO (salta riga di titolo) ----
        try:
            df = pd.read_excel(
                io.BytesIO(response.content),
                skiprows=righe_da_saltare,
                sheet_name=0
            )
        except Exception as e:
            print(f"[ERROR] \t Impossibile leggere {file_name}: {e} -> SALTATO (non spostato)")
            continue

        if nome_colonna_data not in df.columns:
            print(f"[WARNING] \t Colonna '{nome_colonna_data}' non trovata in {file_name} -> SALTATO (non spostato)")
            continue

        # ---- CONTROLLO DATE ----
        date_series = pd.to_datetime(df[nome_colonna_data], errors="coerce", dayfirst=True)

        if date_series.isna().all():
            print(f"[WARNING] \t Nessuna data valida trovata in {file_name} -> SALTATO (non spostato)")
            continue

        date_valide = date_series.dropna()
        anni = date_valide.dt.year.unique()
        mesi = date_valide.dt.month.unique()

        conforme = (len(anni) == 1 and len(mesi) == 1)

        if conforme:
            anno = str(int(anni[0]))
            mese_str = str(int(mesi[0])).zfill(2)
            nuovo_nome = get_raw_name(anno, mese_str)
            nuovo_path = f"{dropbox_folder_destinazione}/{nuovo_nome}"
            
            file_dict = {
                "anno": anno,
                "mese_str": mese_str,
                "raw_name": nuovo_nome,
                "raw_path": nuovo_path
            }
            file_smistati["SMISTATI"].append(file_dict)
        else:
            if contatore_broken == 0:
                nuovo_nome = f"{target_broken_name}{estesione_files}"
            else:
                nuovo_nome = f"{target_broken_name}_{contatore_broken}{estesione_files}"
            contatore_broken += 1

            print(f"[WARNING] \t {file_name} contiene date di anni/mesi diversi -> rinominato in {nuovo_nome}")
            nuovo_path = f"{dropbox_folder_origine}/{nuovo_nome}"
            
            file_dict = {
                "anno": None,
                "mese_str": None,
                "raw_name": nuovo_nome,
                "raw_path": nuovo_path
            }
            file_smistati["BROKEN"].append(file_dict)

        # ---- CONTROLLO ESISTENZA DESTINAZIONE ----
        try:
            dbx.files_get_metadata(nuovo_path)
            esiste_destinazione = True
        except ApiError:
            esiste_destinazione = False

        if esiste_destinazione:
            if not flag_sovrascrivi_raw:
                print(f"[WARNING] \t {nuovo_path} esiste già -> SALTATO (usa flag_sovrascrivi=True per sovrascrivere)")
                continue
            else:
                dbx.files_delete_v2(nuovo_path)
                print(f"[INFO] \t {nuovo_path} esistente eliminato per sovrascrittura")

        # ---- SPOSTAMENTO / RINOMINA ----
        try:
            dbx.files_move_v2(dropbox_path, nuovo_path)
            etichetta = "CONFORME" if conforme else "NON CONFORME"
            print(f"[OK] \t [{etichetta}] {file_name} -> {nuovo_path}")
        except ApiError as e:
            print(f"[ERROR] \t Impossibile spostare {file_name}: {e}")


    return file_smistati