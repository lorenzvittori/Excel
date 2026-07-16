from typing import Any
from typing import cast
import configuration as config
import logger
from DROPBOX import dropbox_module as db_module
import pandas as pd
import configuration as config
from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module         as gd_module
from ELABORATION    import processing_module    as pr_module
from datetime       import datetime
from typing import cast
import configuration as config 
import pandas as pd
import os
import logger
from pathlib import Path


def smista_dropbox(
    *,
    dbx: Any,
    dropbox_folder_origine: str,
    dropbox_folder_destinazione: str,
    target_broken_name: str,
    nome_colonna_data: str,
    righe_da_saltare: int,
    flag_sovrascrivi_raw: bool,
    get_raw_name
) -> list[dict[str, str]]:
    """
    Smista i file Excel presenti nella cartella Dropbox di origine.

    Restituisce una lista del tipo:
        [
            {"anno": "2026", "mese_str": "06"},
            {"anno": "2026", "mese_str": "07"},
        ]

    Solleva SystemExit se non viene trovato alcun file valido.
    """

    logger.new_phase("Smistamento dei file")

    risultato = db_module.smista_file_excel(
        dbx=dbx,
        dropbox_folder_destinazione=dropbox_folder_destinazione,
        dropbox_folder_origine=dropbox_folder_origine,
        get_raw_name=get_raw_name,
        estesione_files=".xlsx",
        target_broken_name=target_broken_name,
        nome_colonna_data=nome_colonna_data,
        righe_da_saltare=righe_da_saltare,
        flag_sovrascrivi_raw=flag_sovrascrivi_raw,
    )

    logger.end_phase()

    lista_anno_mese = risultato["SMISTATI"]

    if not lista_anno_mese:
        logger.error_mex("Nessun file conforme trovato da smistare")
        raise SystemExit

    return lista_anno_mese



def download_dropbox(
    *,
    dbx,
    anno: str,
    mese: str,
    dropbox_raw_folder: str,
    dropbox_prc_folder: str,
    foglio_spese: str,
    foglio_entrate: str,
    prioritizza_prc: bool = False,
) -> dict[str, pd.DataFrame]:

    logger.new_phase("DROPBOX - Download")

    nome_raw = config.get_raw_name(
        anno=anno,
        mese_str=mese,
    )

    nome_prc = config.get_prc_name(
        anno=anno,
        mese_str=mese,
    )

    # ------------------------------------------------------------------
    # Controllo presenza file
    # ------------------------------------------------------------------

    logger.new_phase("Controllo presenza dei files")

    raw_disponibili = [
        f.name
        for f in dbx.files_list_folder(str(dropbox_raw_folder)).entries
    ]

    if nome_raw in raw_disponibili:
        logger.info_mex(f"Trovato file RAW: {dropbox_raw_folder}/{nome_raw}")
    else:
        logger.error_mex(
            corpo="File RAW inesistente",
            dettaglio=f"{dropbox_raw_folder}/{nome_raw}",
        )
        raise ValueError

    prc_disponibili = [
        f.name
        for f in dbx.files_list_folder(str(dropbox_prc_folder)).entries
    ]

    if nome_prc in prc_disponibili:
        logger.info_mex(f"Trovato file PROCESSED: {dropbox_prc_folder}/{nome_prc}")
    else:
        logger.info_mex("File PROCESSED inesistente")

    logger.end_phase()

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    if prioritizza_prc:

        logger.info_mex("USO IL FILE PROCESSED")

        dataframe = db_module.get_dataframe_from_dropbox(
            dbx=dbx,
            dropbox_folder=dropbox_prc_folder,
            file_name=nome_prc,
            header=0,
        )

    else:

        logger.info_mex("USO IL FILE RAW")

        dataframe = db_module.get_dataframe_from_dropbox(
            dbx=dbx,
            dropbox_folder=dropbox_raw_folder,
            file_name=nome_raw,
        )

    # ------------------------------------------------------------------
    # Validazione
    # ------------------------------------------------------------------

    if isinstance(dataframe, pd.DataFrame):
        logger.error_mex(
            f"Non esistono i fogli {foglio_spese} e {foglio_entrate}"
        )
        raise ValueError

    dataframe = cast(dict[str, pd.DataFrame], dataframe)

    if foglio_spese not in dataframe:
        logger.error_mex(f"Non esiste il foglio {foglio_spese}")
        raise ValueError

    if foglio_entrate not in dataframe:
        logger.error_mex(f"Non esiste il foglio {foglio_entrate}")
        raise ValueError

    logger.end_all_phases()

    return dataframe



def elabora_spese_entrate(
    df_raw: dict[str, pd.DataFrame], 
    anno, 
    mese_str: str, 
    design,
    path_csv_add_rows: Path,
    flag_stampa_duplicati: bool,
    flag_stampa_spese_altro: bool) -> dict[str, pd.DataFrame]:
    
    logger.new_phase("Pulizia e formattazione della tabella")

    PRC_DATAFRAME = pr_module.processa_dataframe(
        df_raw=df_raw,
        anno=anno,
        mese_str=mese_str,
        design = design,
        path_csv_add_rows= path_csv_add_rows,
        flag_stampa_duplicati = flag_stampa_duplicati,
        flag_stampa_spese_altro = flag_stampa_spese_altro)

    logger.ok_mex("Elaborazione: ✔ COMPLETATA")
    logger.end_phase()   # chiude "Pulizia e formattazione della tabella"

    return PRC_DATAFRAME


def scrivi__su_sheet(
    client, 
    df_spese_prc: pd.DataFrame, 
    design, 
    anno, 
    mese_str: str, 
    flag_sovrascrivi_celle: bool,
    df_entrate_prc: pd.DataFrame, 
    config,) -> None:
    
    logger.new_phase("Scrittura SPESE su GoogleSheet")
    gd_module.sync_spese_mensili(
        client = client,
        df_spese_prc = df_spese_prc,
        flag_sovrascrivi_celle = flag_sovrascrivi_celle,
        id_google_sheet = config.ID_GOOGLE_SHEET[anno],
        nome_foglio_mese = config.MESI[mese_str]["nome_foglio_associato"],
        num_col_sheet_spese = design.num_col_spese_PRC(),
        cell_spese_first_entry = design.CELLA_SPESE_FIRST_ENTRY,
        cell_spese_timestamp = design.CELLA_SPESE_TSTAMP
    )
    logger.ok_mex(f"Scrittura delle spese: ✔ COMPLETATA")
    logger.end_phase()   # chiude "Scrittura SPESE su GoogleSheet"


    logger.new_phase("Scrittura ENTRATE su GoogleSheet")

    # ---- AGGIUNTA TIMESTAMP ENTRATE: stesso istante per tutte le righe di questa run ----
    timestamp_run = datetime.now().strftime("%d/%m/%Y %H.%M.%S")
    df_entrate_prc["TimeStamp"] = timestamp_run
    logger.info_mex(f"TimeStamp entrate: {timestamp_run}")

    colonne_entrate_attuali = sorted(df_entrate_prc.columns)
    colonne_entrate_attese = sorted(design.colonne_entrate_PRC())

    if colonne_entrate_attuali != colonne_entrate_attese:
        logger.error_mex(
            corpo = "Colonne nel foglio entrate non corrispondenti a quelle attese",
            dettaglio = [ f"colonne attuali : {colonne_entrate_attuali}",
                        f"colonne attese : {colonne_entrate_attese}"])
        raise ValueError()


    gd_module.sync_entrate_totali(
        client = client,
        anno = anno,
        mese_str = mese_str,
        col_mese    =   design.entrate.mese.sheet,
        col_data    =   design.entrate.data.sheet,
        col_importo =   design.entrate.importo.sheet,
        col_note    =   design.entrate.note.sheet,
        col_timestamp = design.entrate.timestamp.sheet,
        top_left_entry = design.CELLA_ENTRATE_FIRST_ENTRY,
        id_google_sheet = config.ID_GOOGLE_SHEET[anno],
        nome_foglio = design.NOME_FOGLIO_TOTAL_ENTRATE,
        df_entrate_prc = df_entrate_prc)

    logger.ok_mex(f"Scrittura delle entrate: ✔ COMPLETATA")
    logger.end_phase()   # chiude "Scrittura ENTRATE su GoogleSheet"