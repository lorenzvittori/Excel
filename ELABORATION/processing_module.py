## NOME FILE: processing_module.py
from    pathlib import Path
from    math    import inf
import pandas as pd
import logger
import configuration as config

# ---------------------------------------- FUNZIONI ----------------------------------------
  # FORMATTAZIONE E PULIZIA
def seleziona_e_rinomina_colonne(df: pd.DataFrame, mappa_colonne: dict, nome_foglio: str) -> pd.DataFrame:
    colonne_mancanti = [
        col for col in mappa_colonne
        if col not in df.columns
    ]

    if colonne_mancanti:
        raise ValueError(
            f"Colonne mancanti nel foglio {nome_foglio}: {colonne_mancanti}"
        )

    return df[list(mappa_colonne.keys())].rename(columns=mappa_colonne)

def formatta_dataframe_output(df: pd.DataFrame, colonna_data: str, colonna_importo: str) -> pd.DataFrame:
    df = df.copy()

    df[colonna_data] = df[colonna_data].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
    )

    df[colonna_importo] = df[colonna_importo].apply(
        lambda x: f"{float(x):.2f}".replace(".", ",") if pd.notnull(x) else ""    
    )

    return df

# SPESE
def aggiungi_righe_spese(
        df_spese: pd.DataFrame, 
        additional_rows_csv: Path, 
        anno: str, 
        mese_str: str,
        design: config.Design) -> pd.DataFrame:
    

    df_nuove_righe_raw = pd.read_csv(additional_rows_csv, skipinitialspace=True)

    df_nuove_righe_raw[design.spese.data.prc] = df_nuove_righe_raw["GiornoData"].apply(
        lambda giorno: f"{str(int(giorno)).zfill(2)}/{mese_str}/{anno}"
    )
    
    df_nuove_righe_raw[design.spese.data.prc] = pd.to_datetime(
        df_nuove_righe_raw[design.spese.data.prc],
        errors="coerce",
        dayfirst=True
    )

    def between(
            this_anno: str,
            this_mese_str: str,
            daANNO_MESE: str,
            aANNO_MESE: str) -> bool:

        if daANNO_MESE == "":
            daANNO, daMESE = -inf, -inf
        else:
            if (len(daANNO_MESE) != 7) or (daANNO_MESE[4] != "-"):
                logger.error_mex(f"Formato non valido per daANNO_MESE: '{daANNO_MESE}'")
                raise ValueError()
            daANNO = int(daANNO_MESE[:4])
            daMESE = int(daANNO_MESE[5:])
            if not (1 <= daMESE <= 12):
                logger.error_mex(f"Mese fuori range in daANNO_MESE: {daMESE}")
                raise ValueError()

        if aANNO_MESE == "":
            aANNO, aMESE = inf, inf
        else:
            if (len(aANNO_MESE) != 7) or (aANNO_MESE[4] != "-"):
                logger.error_mex(f"Formato non valido per aANNO_MESE: '{aANNO_MESE}'")
                raise ValueError()
            aANNO = int(aANNO_MESE[:4])
            aMESE = int(aANNO_MESE[5:])
            if not (1 <= aMESE <= 12):
                logger.error_mex(f"Mese fuori range in aANNO_MESE: {aMESE}")
                raise ValueError()

        MESE = int(this_mese_str)
        ANNO = int(this_anno)

        if not (1 <= MESE <= 12):
            logger.error_mex(f"Mese fuori range: {MESE}")
            raise ValueError()

        if (daANNO, daMESE) > (aANNO, aMESE):
            logger.error_mex(f"Intervallo non valido: da ({daANNO},{daMESE}) è dopo a ({aANNO},{aMESE})")
            raise ValueError()
        

        return (daANNO, daMESE) <= (ANNO, MESE) <= (aANNO, aMESE)

    # ---- FILTRA LE RIGHE IN BASE ALL'INTERVALLO daANNO_MESE / aANNO_MESE ----
    maschera = df_nuove_righe_raw.apply(
        lambda row: between(
            this_anno     = anno,
            this_mese_str = mese_str,
            daANNO_MESE   = str(row["daANNO_MESE"]).strip() if pd.notnull(row["daANNO_MESE"]) else "",
            aANNO_MESE    = str(row["aANNO_MESE"]).strip()  if pd.notnull(row["aANNO_MESE"])  else ""
        ),
        axis=1
    )

    df_nuove_righe_filtered = df_nuove_righe_raw[maschera]
    
    nuove_righe = df_nuove_righe_filtered[
        [design.spese.data.prc,
         design.spese.categoria.prc,
         design.spese.importo.prc,
         design.spese.note.prc]
    ].copy()
    

    df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)
    
    dettaglio = nuove_righe.to_string(index=False).split("\n")
   
    logger.info_mex("Righe aggiunte:", dettaglio=dettaglio)
                        
                        
    return df_spese

def prepara_spese(
        df_spese_raw: pd.DataFrame, #senza header
        additional_rows_csv: Path, 
        anno: str, 
        mese_str: str,
        design: config.Design) -> pd.DataFrame:
    
    NOME_FOGLIO_SPESE = design.NOME_FOGLIO_SPESE

    #ELIMINAZIONE DELLA PRIMA RIGA E DICHIARAZIONE DELL'INTESTAZIONE
    df_spese_raw.columns = df_spese_raw.iloc[1]                 #dichiara intestazione
    df_spese_raw.columns.name = None                            #pulisce l'intestazione
    df_spese_raw = df_spese_raw.iloc[2:].reset_index(drop=True) #ignora le prime due righe per i dati


    df_spese = seleziona_e_rinomina_colonne(
        df=df_spese_raw,
        mappa_colonne = design.map_spese_RAWtoPRC(),
        nome_foglio=NOME_FOGLIO_SPESE
    )

    #Aggiunta di nuove righe
    logger.new_phase("Aggiunta righe dal csv")
    
    df_spese = aggiungi_righe_spese(
        df_spese=df_spese,
        additional_rows_csv=additional_rows_csv,
        anno=anno,
        mese_str=mese_str,
        design=design
    )
    logger.end_phase()
    
    # FORMATTAZIONE COLONNA DATA
    df_spese[design.spese.data.prc] = pd.to_datetime(df_spese[design.spese.data.prc],errors="coerce",dayfirst=True)
    
    #PULISCI COLONNA_NOTE
    col = design.spese.note.prc

    df_spese[col] = (
        df_spese[col]
            .astype("string")
            .str.replace("\n", ", ", regex=False)
            .str.strip()
    )
    
    
    # INSERISCI ANNO e MESE
    df_spese.insert(0, design.spese.anno.prc, str(anno))
    df_spese.insert(1, design.spese.mese.prc, int(mese_str))
    
    df_spese.sort_values(by=design.spese.data.prc, inplace=True)
    
    return df_spese

# ENTRATE
def prepara_entrate(
    df_entrate_raw: pd.DataFrame,
    anno: str,
    mese_str: str, 
    design: config.Design) -> pd.DataFrame:

    df_entrate_raw.columns = df_entrate_raw.iloc[1]                 #dichiara intestazione
    df_entrate_raw.columns.name = None                              #pulisce l'intestazione
    df_entrate_raw = df_entrate_raw.iloc[2:].reset_index(drop=True) #ignora le prime due righe per i dati

    #Pulizia

    df_entrate = seleziona_e_rinomina_colonne(
        df=df_entrate_raw,
        mappa_colonne= design.map_entrate_RAWtoPRC(),
        nome_foglio = design.NOME_FOGLIO_ENTRATE
    )

    # FORMATTAZIONE DATA
    df_entrate[design.entrate.data.prc] = pd.to_datetime(df_entrate[design.entrate.data.prc],errors="coerce",dayfirst=True)

        #PULISCI COLONNA NOTE
    df_entrate[design.entrate.note.prc] = (df_entrate[design.entrate.note.prc].astype(str).str.replace("\n", ", ", regex=False).str.strip())

    # INSERISCI ANNO e MESE
    df_entrate.insert(0, design.entrate.anno.prc, str(anno))
    df_entrate.insert(1, design.entrate.mese.prc, int(mese_str))


    df_entrate.sort_values(by=design.entrate.data.prc, inplace=True)

    return df_entrate

# CONTROLLI
def stampa_duplicati(df: pd.DataFrame, nome_tabella: str):
    duplicati = df[df.duplicated(keep=False)]

    if not duplicati.empty:
        dettaglio = duplicati.to_string(index=False).split("\n")
        logger.warning_mex(
            corpo=f"Duplicati trovati nella tabella {nome_tabella.upper()}",
            dettaglio=dettaglio
        )
    else:
        logger.info_mex(f"{nome_tabella.upper()} senza duplicati")

def stampa_spese_altro(df_spese: pd.DataFrame, design: config.Design):
    spese_altro = df_spese[
        df_spese[design.spese.categoria.prc].astype(str).str.strip().str.lower() == "altro"
    ]

    if not spese_altro.empty:
        dettaglio = spese_altro.sort_values(by=design.spese.data.prc).to_string(index=False).split("\n")
        logger.info_mex(
            corpo="Spese con categoria \"Altro\"",
            dettaglio=dettaglio
        )
    else:
        logger.info_mex("Nessuna spesa con categoria \"Altro\".")

# ------------------------------------- FUNZIONE PRINCIPALE -------------------------------------
def processa_dataframe(
        df_raw: dict[str, pd.DataFrame],
        anno: str, 
        mese_str: str,
        design: config.Design,
        path_csv_add_rows: Path,
        flag_stampa_duplicati: bool = False,
        flag_stampa_spese_altro: bool = False) -> dict[str, pd.DataFrame]:
     
    
    NOME_FOGLIO_SPESE   = design.NOME_FOGLIO_SPESE
    NOME_FOGLIO_ENTRATE = design.NOME_FOGLIO_ENTRATE

    
    if not path_csv_add_rows.exists():
        logger.error_mex(f"{path_csv_add_rows} MANCANTE")
        raise SystemExit
    
    
    # -- SPESE --
    logger.new_phase("Elaborazione SPESE")
    df_spese_raw = pd.DataFrame(df_raw[NOME_FOGLIO_SPESE])  
    

    df_spese_wip = prepara_spese(
        df_spese_raw=df_spese_raw,
        additional_rows_csv=path_csv_add_rows,
        anno=anno,
        mese_str=mese_str,
        design=design)


    if flag_stampa_duplicati:
        stampa_duplicati(df_spese_wip, NOME_FOGLIO_SPESE)
    
    if flag_stampa_spese_altro: 
        stampa_spese_altro(df_spese_wip, design)
        
    # Formattazione finale per output Excel
    df_spese_prc = formatta_dataframe_output(
        df = df_spese_wip, 
        colonna_data = design.spese.data.prc, 
        colonna_importo = design.spese.importo.prc)
    
    logger.ok_mex("Elaborazione spese: ✔ COMPLETATA")
    logger.end_phase()
    
    # -- ENTRATE --
    logger.new_phase("Elaborazione ENTRATE")
    df_entrate_raw = pd.DataFrame(df_raw[NOME_FOGLIO_ENTRATE])

    df_entrate_wip = prepara_entrate(
        df_entrate_raw=df_entrate_raw,
        anno = anno,
        mese_str=mese_str,
        design=design)
    
    if flag_stampa_duplicati:
        stampa_duplicati(df_entrate_wip, NOME_FOGLIO_ENTRATE)
    
    # Formattazione finale per output Excel
    df_entrate_prc = formatta_dataframe_output(
        df = df_entrate_wip, 
        colonna_data = design.entrate.data.prc, 
        colonna_importo = design.entrate.importo.prc)
    
    logger.ok_mex("Elaborazione entrate: ✔ COMPLETATA")
    logger.end_phase()
    return {
        NOME_FOGLIO_SPESE: df_spese_prc,
        NOME_FOGLIO_ENTRATE: df_entrate_prc
    }