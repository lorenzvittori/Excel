## NOME FILE: FLUSSO_TOTALE.py
from DROPBOX import dropbox_module as db_module
from GOOGLE_DRIVE import write_module as gd_module
from pathlib import Path
from typing import cast
import processing_module as pr_module
import configuration as config  
import pandas as pd
import os
import logger


FLAG_AUTO_ANNO_MESE = os.getenv("FLAG_AUTO_ANNO_MESE", "false").lower() == "true"
ANNO = os.getenv("ANNO", "2026")
MESE = os.getenv("MESE", "07")

if not FLAG_AUTO_ANNO_MESE and (not ANNO or not MESE):
    logger.tipo_messaggio(
        tipo = "ERROR",
        corpo= "Input non validi"
    )
    raise SystemExit


STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.DESIGN
NOMI_COLONNE_APP        = config.NOMI_COLONNE_APP

FLAG_SOVRASCRIVI_SHEET = True


if __name__ == "__main__":
    #DOWNLOAD FILE DAL DROPBOX
    #fase 0
    logger.reset_fase()
    
    DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
    DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
    
    DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
    DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
    
    LOCAL_RAW_FOLDER = STRUTTURA_REPOSITORY["FOLD_RAW_TBT"]
    LOCAL_PRC_FOLDER = STRUTTURA_REPOSITORY["FOLD_PRC_TBT"]
    
    FOGLIO_SPESE = DESIGN["NOME_FOGLIO_SPESE"]
    FOGLIO_ENTRATE = DESIGN["NOME_FOGLIO_ENTRATE"]
    
    logger.fase("DROPBOX")
    logger.inizio_istanza("Connessione al DropBox")
    
    dbx = db_module.get_dropbox_client(
        dropbox_credential = DROPBOX_CRED,
        dropbox_token = DROPBOX_TOKEN
    )
    
    logger.fine_istanza()
    
    if FLAG_AUTO_ANNO_MESE:
        
        logger.inizio_istanza("Smistamento dei file sul DropBox")
        FILE_SMISTATI = db_module.smista_file_excel(
            dbx=dbx,
            dropbox_folder_destinazione=DROPBOX_RAW_FOLDER,
            dropbox_folder_origine="",
            get_raw_name=config.get_raw_name,
            estesione_files=".xlsx",
            target_broken_name="BROKEN",
            nome_colonna_data=NOMI_COLONNE_APP["COLONNE_SPESE"]["COL_SPESE_DATA"],
            righe_da_saltare=1,
            flag_sovrascrivi=True,
        )
        logger.fine_istanza()
        LIST_ANNO_MESE = FILE_SMISTATI["SMISTATI"]

        if not LIST_ANNO_MESE:
            logger.tipo_messaggio("ERRORE", "Nessun file conforme trovato da smistare")
            raise SystemExit
    else:
        LIST_ANNO_MESE = [{
                "anno": ANNO,
                "mese_str": MESE}]


    ERRORI = []

    for x in LIST_ANNO_MESE:
        
        ANNO = x["anno"]
        MESE = x["mese_str"]
        
        logger.reset_fase()
        
        try:
            logger.separatore()
            logger.titolo(anno = ANNO, mese_str = MESE)
            logger.fase("DROPBOX")

            NAME_RAW_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
            NAME_PROCESSED_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)

            RAW_DATAFRAME = db_module.get_dataframe_from_dropbox(
                dbx = dbx,
                dropbox_folder = DROPBOX_RAW_FOLDER,
                file_name = NAME_RAW_FILE
            )

            if isinstance(RAW_DATAFRAME, pd.DataFrame):
                raise ValueError("Non ci sono i fogli SPESE ed ENTRATE")

            RAW_DATAFRAME = cast(dict[str, pd.DataFrame], RAW_DATAFRAME)

            if FOGLIO_SPESE not in RAW_DATAFRAME.keys():
                raise ValueError(f"Non è presente il foglio {FOGLIO_SPESE} nell'excel")

            if FOGLIO_ENTRATE not in RAW_DATAFRAME.keys():
                raise ValueError(f"Non è presente il foglio {FOGLIO_ENTRATE} nell'excel")


            #PROCESSA MESE
            logger.fase("Pulizia e formattazione della tabella")

            logger.sottofase("Pulizia e formattazione")
            PRC_DATAFRAME = pr_module.processa_dataframe(
                df_raw=RAW_DATAFRAME,
                anno=ANNO,
                mese_str=MESE,
                design = DESIGN,
                struttura_repo = STRUTTURA_REPOSITORY,
                colonne_app = NOMI_COLONNE_APP,
                flag_blocca_se_input_manca = True, 
                flag_sovrascrivi_output = False,
                flag_stampa_percorsi = False,
                flag_stampa_duplicati = False,
                flag_processa_tutti_i_mesi = False,
                flag_stampa_spese_altro = False)

            
            #SCRITTURA SU GOOGLE DRIVE
            logger.fase("GOOGLE DRIVE")

            GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]
            
            logger.inizio_istanza("Connessione a Google Drive")
            client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
            logger.fine_istanza()
            

            #Controlla che il file spese abbia le giuste colonne:
            PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]

            colonne_spese_attuali = sorted(PRC_SPESE_DATAFRAME.columns)
            colonne_spese_attese = sorted([DESIGN[c] for c in NOMI_COLONNE_APP["COLONNE_SPESE"].keys()])

            if colonne_spese_attuali != colonne_spese_attese:
                logger.tipo_messaggio(
                        tipo = "ERRORE", 
                        corpo=  "Colonne nel foglio spese non corrispondenti a quelle attese",
                        dettaglio=[ f"colonne attuali : {colonne_spese_attuali}",
                                    f"colonne attese : {colonne_spese_attese}"])
                raise ValueError()

            
            logger.inizio_istanza("Scrittura su sheet")
            gd_module.sync_month_local(
                client=client,
                anno=ANNO,
                mese_str=MESE,
                df_prc=PRC_DATAFRAME,
                flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET
            )
            logger.fine_istanza()
            
            logger.inizio_istanza("Salvataggio della tabella processata")
            db_module.upload_dataframe_to_dropbox(
                dbx = dbx,
                dropbox_folder = DROPBOX_PRC_FOLDER,
                file_name = NAME_PROCESSED_FILE,
                df = PRC_DATAFRAME,
                flag_sovrascrivi = True
            )
            logger.fine_istanza()
            logger.fine(anno = ANNO, mese_str=MESE)
            logger.separatore()

        except Exception as e:
            print(f"[ERROR]\t Fallito il flusso per ANNO {ANNO} - MESE {MESE}: {e}")
            ERRORI.append((ANNO, MESE, str(e)))
            continue


    logger.separatore()
    if ERRORI:
        log_errori = []
        for anno_err, mese_err, errore in ERRORI:
            log_errori.append(f"ANNO {anno_err} MESE {mese_err}: {errore}")
        
        logger.tipo_messaggio(
                tipo = "WARNING",
                corpo = f"{len(ERRORI)} su {len(LIST_ANNO_MESE)} file hanno fallito:",
                dettaglio=log_errori)
        
        logger.separatore()
        raise SystemExit
    else:
        logger.tipo_messaggio(tipo = "INFO", corpo = f"Tutti i {len(LIST_ANNO_MESE)} file sono stati processati con successo")
        logger.separatore()
        