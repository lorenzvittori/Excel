import pandas as pd
from pathlib import Path
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
            f"[ERROR]\t- Colonne mancanti nel foglio {nome_foglio}: {colonne_mancanti}"
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
        design: dict) -> pd.DataFrame:
    df_nuove_righe_raw = pd.read_csv(additional_rows_csv)

    df_nuove_righe_raw[design["COL_SPESE_DATA"]] = df_nuove_righe_raw["GiornoData"].apply(
        lambda giorno: f"{str(int(giorno)).zfill(2)}/{mese_str}/{anno}"
    )
    
    df_nuove_righe_raw[design["COL_SPESE_DATA"]] = pd.to_datetime(
        df_nuove_righe_raw[design["COL_SPESE_DATA"]],
        errors="coerce",
        dayfirst=True
    )

    nuove_righe = df_nuove_righe_raw[
        [design["COL_SPESE_DATA"], design["COL_SPESE_CATEGORIA"], design["COL_SPESE_IMPORTO"]]
    ].copy()

    nuove_righe[design["COL_SPESE_NOTE"]] = ""

    df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)

    return df_spese

def prepara_spese(
        df_spese_raw: pd.DataFrame, #senza header
        additional_rows_csv: Path, 
        anno: str, 
        mese_str: str,
        design: dict,
        colonne_app_spese: dict) -> pd.DataFrame:
    
    NOME_FOGLIO_SPESE = design["NOME_FOGLIO_SPESE"]

    #ELIMINAZIONE DELLA PRIMA RIGA E DICHIARAZIONE DELL'INTESTAZIONE
    df_spese_raw.columns = df_spese_raw.iloc[1]                 #dichiara intestazione
    df_spese_raw.columns.name = None                            #pulisce l'intestazione
    df_spese_raw = df_spese_raw.iloc[2:].reset_index(drop=True) #ignora le prime due righe per i dati

    mappa_colonne_spese = {colonne_app_spese[k]: design[k] for k in colonne_app_spese}

    df_spese = seleziona_e_rinomina_colonne(
        df=df_spese_raw,
        mappa_colonne=mappa_colonne_spese,
        nome_foglio=NOME_FOGLIO_SPESE
    )

    #Aggiunta di nuove righe
    df_spese = aggiungi_righe_spese(
        df_spese=df_spese,
        additional_rows_csv=additional_rows_csv,
        anno=anno,
        mese_str=mese_str,
        design=design
    )
    
    # FORMATTAZIONE DATA
    df_spese[design["COL_SPESE_DATA"]] = pd.to_datetime(df_spese[design["COL_SPESE_DATA"]],errors="coerce",dayfirst=True)
    
    
    df_spese.sort_values(by=design["COL_SPESE_DATA"], inplace=True)
    
    return df_spese

# ENTRATE
def prepara_entrate(
    df_entrate_raw: pd.DataFrame,
    mese_str: str, 
    design: dict,
    colonne_app_entrate: dict) -> pd.DataFrame:

    df_entrate_raw.columns = df_entrate_raw.iloc[1]                 #dichiara intestazione
    df_entrate_raw.columns.name = None                              #pulisce l'intestazione
    df_entrate_raw = df_entrate_raw.iloc[2:].reset_index(drop=True) #ignora le prime due righe per i dati

    #Pulizia
    mappa_colonne_entrate = {colonne_app_entrate[k]: design[k] for k in colonne_app_entrate}

    df_entrate = seleziona_e_rinomina_colonne(
        df=df_entrate_raw,
        mappa_colonne=mappa_colonne_entrate,
        nome_foglio="Entrate"
    )

    # FORMATTAZIONE DATA
    df_entrate[design["COL_ENTRATE_DATA"]] = pd.to_datetime(df_entrate[design["COL_ENTRATE_DATA"]],errors="coerce",dayfirst=True)

    df_entrate.insert(0, design["COL_ENTRATE_MESE"], int(mese_str))

    df_entrate.sort_values(by=design["COL_ENTRATE_DATA"], inplace=True)

    return df_entrate

# CONTROLLI
def stampa_duplicati(df: pd.DataFrame, nome_tabella: str):
    duplicati = df[df.duplicated(keep=False)]

    if not duplicati.empty:
        print(f"\n\t[WARNING]\t DUPLICATI TROVATI NELLE {nome_tabella.upper()}:")
        print("\t" +duplicati.to_string(index=False).replace("\n", "\n\t"))
    else:
        print(f"\n\t[INFO]\t {nome_tabella.upper()} senza duplicati")

def stampa_spese_altro(df_spese: pd.DataFrame, design: dict):
    spese_altro = df_spese[
        df_spese[design["COL_SPESE_CATEGORIA"]].astype(str).str.strip().str.lower() == "altro"
    ]

    if not spese_altro.empty:
        print(f"\n[INFO]\t SPESSE CON CATEGORIA \"ALTRO\":")
        print("\t" + spese_altro.sort_values(by=design["COL_SPESE_DATA"]).to_string(index=False).replace("\n","\n\t"))
    else:
        print(f"[INFO]\t Nessuna spesa con categoria \"Altro\".")

# ------------------------------------- FUNZIONE PRINCIPALE -------------------------------------
def processa_dataframe(
        df_raw: dict[str, pd.DataFrame],
        anno: str, 
        mese_str: str,
        design: dict,
        struttura_repo: dict,
        colonne_app: dict,
        flag_blocca_se_input_manca: bool = True, 
        flag_sovrascrivi_output: bool = False,
        flag_stampa_percorsi: bool = False,
        flag_stampa_duplicati: bool = False,
        flag_processa_tutti_i_mesi: bool = False,
        flag_stampa_spese_altro: bool = False) -> dict[str, pd.DataFrame]:
     
    
    NOME_FILE_RAW = config.get_raw_name(anno = anno, mese_str = mese_str)
    NOME_FILE_PRC = config.get_prc_name(anno = anno, mese_str = mese_str)
    NOME_FOGLIO_SPESE   = design["NOME_FOGLIO_SPESE"]
    NOME_FOGLIO_ENTRATE = design["NOME_FOGLIO_ENTRATE"]
    DIRECTORY_FILE_RAW      = struttura_repo["FOLD_RAW_TBT"] / NOME_FILE_RAW
    DIRECTORY_FILE_PRC      = struttura_repo["FOLD_PRC_TBT"] / NOME_FILE_PRC
    DIRECTORY_FILE_ADD_ROWS = struttura_repo["FILE_ADD_ROWS"]

    if not DIRECTORY_FILE_RAW.exists():
        print(f"\t[ERROR]\t {NOME_FILE_RAW} MANCANTE", end="")
        raise SystemExit
    
    if not DIRECTORY_FILE_ADD_ROWS.exists():
        print(f"\t[ERROR]\t {DIRECTORY_FILE_ADD_ROWS} MANCANTE", end="")
        raise SystemExit
    
    if flag_stampa_percorsi and not flag_processa_tutti_i_mesi:
        print("\nPercorsi dei file:")
        print(f"\tInput:\t{DIRECTORY_FILE_RAW}")
        print(f"\tOutput:\t{DIRECTORY_FILE_PRC}")
        
    df_spese_raw = pd.DataFrame(df_raw[NOME_FOGLIO_SPESE])  # Salta la prima riga che contiene il titolo del foglio
    df_entrate_raw = pd.DataFrame(df_raw[NOME_FOGLIO_ENTRATE])

    df_spese_wip = prepara_spese(
        df_spese_raw=df_spese_raw,
        additional_rows_csv=DIRECTORY_FILE_ADD_ROWS,
        anno=anno,
        mese_str=mese_str,
        design=design,
        colonne_app_spese=colonne_app["COLONNE_SPESE"]
    )

    df_entrate_wip = prepara_entrate(
        df_entrate_raw=df_entrate_raw,
        mese_str=mese_str,
        design=design,
        colonne_app_entrate=colonne_app["COLONNE_ENTRATE"]
    )

    if flag_stampa_duplicati and not flag_processa_tutti_i_mesi:
        stampa_duplicati(df_spese_wip, NOME_FOGLIO_SPESE)
        stampa_duplicati(df_entrate_wip, NOME_FOGLIO_ENTRATE)
    
    if flag_stampa_spese_altro and not flag_processa_tutti_i_mesi: 
        stampa_spese_altro(df_spese_wip, design)

    # Formattazione finale per output Excel
    
    df_spese_prc = formatta_dataframe_output(df_spese_wip, colonna_data=design["COL_SPESE_DATA"], colonna_importo=design["COL_SPESE_IMPORTO"])
    df_entrate_prc = formatta_dataframe_output(df_entrate_wip, colonna_data=design["COL_ENTRATE_DATA"], colonna_importo=design["COL_ENTRATE_IMPORTO"])
    
    return {
        NOME_FOGLIO_SPESE: df_spese_prc,
        NOME_FOGLIO_ENTRATE: df_entrate_prc
    }