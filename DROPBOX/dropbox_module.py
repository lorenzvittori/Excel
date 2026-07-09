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
            logger.error_mex(
                corpo="File credenziali DropBox non trovato",
                dettaglio=f"{DROPBOX_CRED}")
            raise FileNotFoundError
        if not DROPBOX_TOKEN.exists():
            logger.error_mex(
                corpo="File token DropBox non trovato",
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
        logger.error_mex("Credenziali non valide")
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
        file_disponibili = [f.name for f in dbx.files_list_folder(str(DROPBOX_FOLDER)).entries]  # type: ignore
        logger.error_mex(
            corpo=f"File non trovato su Dropbox: {DROPBOX_DIR}",
            dettaglio=["File disponibili nella cartella remota:"] + file_disponibili
        )
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- DOWNLOAD IN MEMORIA -----
    _, response = dbx.files_download(DROPBOX_DIR)           # type: ignore
    logger.info_mex(f"File letto da Dropbox: {DROPBOX_DIR}")

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
        file_disponibili = [f.name for f in dbx.files_list_folder(DROPBOX_FOLDER).entries]  # type: ignore
        logger.error_mex(
            corpo=f"File non trovato su Dropbox: {DROPBOX_DIR}",
            dettaglio=["File disponibili nella cartella remota:"] + file_disponibili
        )
        raise FileNotFoundError(f"File non presente su Dropbox: {DROPBOX_DIR}")

    # ---- CHECK LOCALE -----
    if not DOWNLOAD_FOLDER.exists():
        logger.error_mex(f"Cartella di destinazione non esistente: {DOWNLOAD_FOLDER}")
        raise FileNotFoundError(f"Cartella di destinazione non esistente: {DOWNLOAD_FOLDER}")

    if OUTPUT_DIR.exists():
        if blocca_se_esistente:
            logger.error_mex(f"File gia' esistente -> Download interrotto: {OUTPUT_DIR}")
            return
        else:
            logger.warning_mex(f"File gia' esistente -> sovrascritto: {OUTPUT_DIR}")

    # ---- DOWNLOAD -----
    dbx.files_download_to_file(str(OUTPUT_DIR), DROPBOX_DIR)
    logger.info_mex(f"Download completato: {OUTPUT_DIR}")
    logger.info_mex(f"File creato in: {OUTPUT_DIR}")


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
    logger.info_mex(f"Upload completato: {DROPBOX_DIR}")
    
    
def smista_file_excel(
        dbx: dropbox.Dropbox,
        dropbox_folder_origine: str,
        dropbox_folder_destinazione: str,
        get_raw_name,
        estesione_files: str = ".xlsx",
        target_broken_name: str = "BROKEN",
        nome_colonna_data: str = "Data e ora",
        righe_da_saltare: int = 1,
        flag_sovrascrivi_raw: bool = False
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
        logger.info_mex(f"Nessun file .xlsx trovato in {dropbox_folder_origine}")
        return {"SMISTATI": [], "BROKEN": []}

    # ---- PULIZIA BROKEN RESIDUI DI RUN PRECEDENTI ----
    file_broken_residui = [
        f for f in file_xlsx
        if f.name.startswith(target_broken_name)
    ]

    if file_broken_residui:
        logger.new_phase("Eliminazione dei broken files esistenti")
        for f in file_broken_residui:
            dbx.files_delete_v2(f"{dropbox_folder_origine}/{f.name}")
            logger.info_mex(f"Rimosso broken residuo: {f.name}")
        logger.end_phase()

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

        logger.new_phase(f"Controllo file: {file_name}")

        # ---- DOWNLOAD ----
        try:
            _, response = dbx.files_download(dropbox_path)  # type: ignore
        except ApiError as e:
            logger.error_mex(f"Impossibile scaricare {file_name}", dettaglio=str(e))
            logger.end_phase()
            continue

        # ---- LETTURA PRIMO FOGLIO (salta riga di titolo) ----
        try:
            df = pd.read_excel(
                io.BytesIO(response.content),
                skiprows=righe_da_saltare,
                sheet_name=0
            )
        except Exception as e:
            logger.error_mex(f"Impossibile leggere {file_name} -> SALTATO (non spostato)", dettaglio=str(e))
            logger.end_phase()
            continue

        if nome_colonna_data not in df.columns:
            logger.warning_mex(f"Colonna '{nome_colonna_data}' non trovata in {file_name} -> SALTATO (non spostato)")
            logger.end_phase()
            continue

        # ---- CONTROLLO DATE ----
        date_series = pd.to_datetime(df[nome_colonna_data], errors="coerce", dayfirst=True)

        if date_series.isna().all():
            logger.warning_mex(f"Nessuna data valida trovata in {file_name} -> SALTATO (non spostato)")
            logger.end_phase()
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

            logger.warning_mex(f"{file_name} contiene date di anni/mesi diversi -> rinominato in {nuovo_nome}")
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
                logger.warning_mex(f"{nuovo_path} esiste già -> SALTATO (usa flag_sovrascrivi_raw=True per sovrascrivere)")
                logger.end_phase()
                continue
            else:
                dbx.files_delete_v2(nuovo_path)
                logger.info_mex(f"{nuovo_path} gia' esistente -> sovrascritto")

        # ---- SPOSTAMENTO / RINOMINA ----
        try:
            dbx.files_move_v2(dropbox_path, nuovo_path)
            etichetta = "CONFORME" if conforme else "NON CONFORME"
            logger.info_mex(f"[{etichetta}] {file_name} -> {nuovo_path}")
        except ApiError as e:
            logger.error_mex(f"Impossibile spostare {file_name}", dettaglio=str(e))

        logger.end_phase()

    return file_smistati





def spacchetta_file_annuale(
        dbx: dropbox.Dropbox,
        dropbox_folder_origine: str,
        file_name: str,
        get_raw_name,
        nome_foglio_spese: str = "Spese",
        nome_foglio_entrate: str = "Entrate",
        nome_colonna_data: str = "Data e ora",
        righe_da_saltare: int = 1,
        riga_titolo_fittizia: str = "elenco per il periodo") -> dict[str, list[dict]]:
    """
    Scarica un file Excel annuale (con fogli Spese ed Entrate, contenenti
    tutte le righe dell'anno) da dropbox_folder_origine, e lo spacchetta
    in 12 file mensili separati (uno per mese, gennaio-dicembre), ciascuno
    con la stessa struttura di un file raw mensile (riga titolo fittizia +
    header + dati), caricati su dropbox_folder_origine con nome
    get_raw_name(anno, mese_str).

    Validazioni:
    - tutte le date nel foglio Spese e nel foglio Entrate devono appartenere
      allo stesso anno (altrimenti la funzione si interrompe con errore)
    - ogni mese da 1 a 12 deve avere almeno una riga nel foglio Spese
      (altrimenti la funzione si interrompe con errore, nessun file viene
      caricato)
    - le Entrate possono avere mesi mancanti (nessun controllo su di esse)
    - eventuali date non parsabili (NaT) nel file annuale sono considerate
      un errore bloccante (possibile file corrotto)

    Al termine, se tutto va a buon fine, il file annuale originale viene
    eliminato da Dropbox.
    """

    dropbox_path = f"{dropbox_folder_origine}/{file_name}"

    logger.new_phase(f"Spacchettamento file annuale: {file_name}")

    # ---- DOWNLOAD ----
    try:
        _, response = dbx.files_download(dropbox_path)  # type: ignore
    except ApiError as e:
        logger.error_mex(f"Impossibile scaricare {file_name}", dettaglio=str(e))
        logger.end_phase()
        raise

    # ---- LETTURA DEI DUE FOGLI (salta riga di titolo) ----
    try:
        df_spese_raw = pd.read_excel(
            io.BytesIO(response.content),
            skiprows=righe_da_saltare,
            sheet_name=nome_foglio_spese
        )
        df_entrate_raw = pd.read_excel(
            io.BytesIO(response.content),
            skiprows=righe_da_saltare,
            sheet_name=nome_foglio_entrate
        )
    except Exception as e:
        logger.error_mex(f"Impossibile leggere {file_name}", dettaglio=str(e))
        logger.end_phase()
        raise

    # ---- CONTROLLO COLONNA DATA ----
    if nome_colonna_data not in df_spese_raw.columns:
        logger.error_mex(f"Colonna '{nome_colonna_data}' non trovata nel foglio {nome_foglio_spese}")
        logger.end_phase()
        raise ValueError(f"Colonna '{nome_colonna_data}' non trovata nel foglio {nome_foglio_spese}")

    if nome_colonna_data not in df_entrate_raw.columns:
        logger.error_mex(f"Colonna '{nome_colonna_data}' non trovata nel foglio {nome_foglio_entrate}")
        logger.end_phase()
        raise ValueError(f"Colonna '{nome_colonna_data}' non trovata nel foglio {nome_foglio_entrate}")

    # ---- CONVERSIONE DATE ----
    date_spese = pd.to_datetime(df_spese_raw[nome_colonna_data], errors="coerce", dayfirst=True)
    date_entrate = pd.to_datetime(df_entrate_raw[nome_colonna_data], errors="coerce", dayfirst=True)

    if date_spese.isna().any():
        logger.error_mex(f"Trovate date non valide nel foglio {nome_foglio_spese} -> file possibilmente corrotto")
        logger.end_phase()
        raise ValueError(f"Date non valide nel foglio {nome_foglio_spese}")

    if date_entrate.isna().any():
        logger.error_mex(f"Trovate date non valide nel foglio {nome_foglio_entrate} -> file possibilmente corrotto")
        logger.end_phase()
        raise ValueError(f"Date non valide nel foglio {nome_foglio_entrate}")

    # ---- CONTROLLO ANNO UNICO (Spese + Entrate insieme) ----
    anni_spese = set(date_spese.dt.year.unique())
    anni_entrate = set(date_entrate.dt.year.unique())
    anni_totali = anni_spese | anni_entrate

    if len(anni_totali) != 1:
        logger.error_mex(
            f"{file_name} contiene date di anni diversi tra Spese ed Entrate",
            dettaglio=[f"Anni trovati: {sorted(anni_totali)}"]
        )
        logger.end_phase()
        raise ValueError(f"Anni multipli trovati in {file_name}: {sorted(anni_totali)}")

    anno = str(anni_totali.pop())

    # ---- CONTROLLO COPERTURA MENSILE (solo Spese) ----
    mesi_spese_presenti = set(date_spese.dt.month.unique())
    mesi_mancanti = set(range(1, 13)) - mesi_spese_presenti

    if mesi_mancanti:
        logger.error_mex(
            f"Il foglio {nome_foglio_spese} non copre tutti i mesi dell'anno {anno}",
            dettaglio=[f"Mesi mancanti: {sorted(mesi_mancanti)}"]
        )
        logger.end_phase()
        raise ValueError(f"Mesi mancanti nel foglio {nome_foglio_spese}: {sorted(mesi_mancanti)}")

    logger.info_mex(f"Anno rilevato: {anno} - Tutti i 12 mesi coperti nel foglio {nome_foglio_spese}")

    # ---- SPACCHETTAMENTO E UPLOAD PER OGNI MESE ----
    file_prodotti = {"SMISTATI": [], "ERRORI": []}

    df_spese_raw = df_spese_raw.copy()
    df_spese_raw["_mese_tmp"] = date_spese.dt.month

    df_entrate_raw = df_entrate_raw.copy()
    df_entrate_raw["_mese_tmp"] = date_entrate.dt.month

    for mese_num in range(1, 13):
        mese_str = str(mese_num).zfill(2)

        logger.new_phase(f"Creazione file mensile {anno}-{mese_str}")

        df_spese_mese = df_spese_raw[df_spese_raw["_mese_tmp"] == mese_num].drop(columns=["_mese_tmp"])
        df_entrate_mese = df_entrate_raw[df_entrate_raw["_mese_tmp"] == mese_num].drop(columns=["_mese_tmp"])

        nuovo_nome = get_raw_name(anno, mese_str)
        nuovo_path = f"{dropbox_folder_origine}/{nuovo_nome}"

        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                _scrivi_foglio_con_titolo_fittizio(
                    writer, df_spese_mese, nome_foglio_spese, riga_titolo_fittizia
                )
                _scrivi_foglio_con_titolo_fittizio(
                    writer, df_entrate_mese, nome_foglio_entrate, riga_titolo_fittizia
                )

            dbx.files_upload(
                buffer.getvalue(), nuovo_path,
                mode=dropbox.files.WriteMode.overwrite  # type: ignore
            )

            logger.info_mex(f"Creato {nuovo_nome}", dettaglio=[
                f"Righe Spese: {len(df_spese_mese)}",
                f"Righe Entrate: {len(df_entrate_mese)}"
            ])

            file_prodotti["SMISTATI"].append({
                "anno": anno,
                "mese_str": mese_str,
                "raw_name": nuovo_nome,
                "raw_path": nuovo_path
            })

        except Exception as e:
            logger.error_mex(f"Impossibile creare/caricare {nuovo_nome}", dettaglio=str(e))
            file_prodotti["ERRORI"].append({"mese_str": mese_str, "errore": str(e)})

        logger.end_phase()

    if file_prodotti["ERRORI"]:
        logger.error_mex(
            f"Spacchettamento incompleto: {len(file_prodotti['ERRORI'])} mesi falliti su 12"
        )
        logger.end_phase()
        raise RuntimeError(f"Spacchettamento incompleto per {file_name}: {len(file_prodotti['ERRORI'])} errori")

    # ---- ELIMINA IL FILE ANNUALE ORIGINALE ----
    try:
        dbx.files_delete_v2(dropbox_path)
        logger.info_mex(f"File annuale originale eliminato: {file_name}")
    except ApiError as e:
        logger.error_mex(f"Impossibile eliminare il file annuale originale {file_name}", dettaglio=str(e))

    logger.end_phase()  # chiude "Spacchettamento file annuale"

    return file_prodotti


def _scrivi_foglio_con_titolo_fittizio(
        writer: pd.ExcelWriter,
        df: pd.DataFrame,
        nome_foglio: str,
        riga_titolo: str) -> None:
    """
    Scrive un DataFrame su un foglio Excel replicando la struttura dei file
    raw originali: una riga di titolo fittizia in cima, poi l'header vero,
    poi i dati - così il file prodotto può essere letto dal resto della
    pipeline con skiprows=1 come un file raw normale.
    """
    n_colonne = len(df.columns)

    # Riga 0: titolo fittizio (solo nella prima cella, resto vuoto)
    riga_titolo_df = pd.DataFrame([[riga_titolo] + [""] * (n_colonne - 1)], columns=df.columns)

    # Riga 1: header vero (i nomi delle colonne come dato, non come intestazione excel)
    header_df = pd.DataFrame([df.columns.tolist()], columns=df.columns)

    df_completo = pd.concat([riga_titolo_df, header_df, df], ignore_index=True)

    df_completo.to_excel(writer, sheet_name=nome_foglio, index=False, header=False)