import pandas as pd
from pathlib import Path


#FORMATO DEI NOMI DEI FILE DI INPUT E OUTPUT
def NOME_INPUT(YYYY, MM): return f"app_{YYYY}_{MM}.xlsx"
def NOME_OUTPUT(YYYY, MM): return f"p_{YYYY}_{MM}.xlsx"


DIZ_MESE_TO_NUMB = {
    "Gennaio": "01",
    "Febbraio": "02",
    "Marzo": "03",
    "Aprile": "04",
    "Maggio": "05",
    "Giugno": "06",
    "Luglio": "07",
    "Agosto": "08",
    "Settembre": "09",
    "Ottobre": "10",
    "Novembre": "11",
    "Dicembre": "12"
}

DIZ_NUMB_TO_MESE = {v: k for k, v in DIZ_MESE_TO_NUMB.items()}

# ---------------------------------------- FUNZIONI ----------------------------------------
# STRUTTURALI
def prepara_percorsi(
        anno: str,
        mese_numb: str,
        structure: dict,
        flag_blocca_se_input_manca: bool = True, 
        flag_sovrascrivi_output: bool = False) -> dict | None:
    
    root_dir = Path(__file__).resolve().parent
    dati_dir = root_dir / structure["MAIN_FOLDER"]
    input_dir = dati_dir / structure["APP_FILE_FOLDER"]
    output_dir = dati_dir / structure["PROCESSED_FOLDER"]

    input_file = input_dir / NOME_INPUT(anno, mese_numb)
    output_file = output_dir / NOME_OUTPUT(anno, mese_numb)
    additional_rows_csv = root_dir / structure["CSV_ADD_ROWS"]

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"\t-!- FILE {NOME_INPUT(anno, mese_numb)} MANCANTE", end="")

        if flag_blocca_se_input_manca:
            print("\n=" * 80)
            print("\nP R O C E S S O   T E R M I N A T O")
            raise SystemExit

        else:
            print(f" -> SALTATO")
            return None

    if not additional_rows_csv.exists():
        print("\t-!- FILE CSV NON TROVATO", end="\t")
        print(f"...{additional_rows_csv}")
        raise SystemExit

    if output_file.exists():
        if not flag_sovrascrivi_output:
            print(f"\t-!- FILE {NOME_OUTPUT(anno, mese_numb)} GIA' ESISTENTE -> IL PROCESSO SI INTERROMPE", end="\t")
            print("=" * 80)
            print("\nP R O C E S S O   T E R M I N A T O")
            raise SystemExit
        else:
            print(f"\t-!- FILE {NOME_OUTPUT(anno, mese_numb)} GIA' ESISTENTE -> SOVRASCRITTO")
            
    return {
        "input_file": input_file,
        "output_file": output_file,
        "additional_rows_csv": additional_rows_csv,
    }

def esporta_excel(df_spese: pd.DataFrame, df_entrate: pd.DataFrame, output_file: Path):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_spese.to_excel(writer, sheet_name="Spese", index=False)
        df_entrate.to_excel(writer, sheet_name="Entrate", index=False)
    
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
        mese_numb: str,
        design: dict) -> pd.DataFrame:
    df_nuove_righe_raw = pd.read_csv(additional_rows_csv)

    df_nuove_righe_raw[design["COL_SPESE_DATA"]] = df_nuove_righe_raw["GiornoData"].apply(
        lambda giorno: f"{str(int(giorno)).zfill(2)}/{mese_numb}/{anno}"
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
        input_file: Path, 
        additional_rows_csv: Path, 
        anno: str, 
        mese_numb: str,
        design: dict,
        colonne_app_spese: dict) -> pd.DataFrame:
    
    #Lettura
    df_spese = pd.read_excel(
        input_file,
        sheet_name="Spese",
        skiprows=1,
        header=0
    )

    #Pulizia
    mappa_colonne_spese = {colonne_app_spese[k]: design[k] for k in colonne_app_spese}

    df_spese = seleziona_e_rinomina_colonne(
        df=df_spese,
        mappa_colonne=mappa_colonne_spese,
        nome_foglio="Spese"
    )

    #Aggiunta di nuove righe
    df_spese = aggiungi_righe_spese(
        df_spese=df_spese,
        additional_rows_csv=additional_rows_csv,
        anno=anno,
        mese_numb=mese_numb,
        design=design
    )
    
    # FORMATTAZIONE DATA
    df_spese[design["COL_SPESE_DATA"]] = pd.to_datetime(df_spese[design["COL_SPESE_DATA"]],errors="coerce",dayfirst=True)
    
    
    df_spese.sort_values(by=design["COL_SPESE_DATA"], inplace=True)
    
    return df_spese

# ENTRATE
def prepara_entrate(
    input_file: Path, 
    mese_numb: str, 
    design: dict,
    colonne_app_entrate: dict) -> pd.DataFrame:
    
    #Lettura 
    df_entrate = pd.read_excel(
        input_file,
        sheet_name="Entrate",
        skiprows=1,
        header=0
    )

    #Pulizia
    mappa_colonne_entrate = {colonne_app_entrate[k]: design[k] for k in colonne_app_entrate}

    df_entrate = seleziona_e_rinomina_colonne(
        df=df_entrate,
        mappa_colonne=mappa_colonne_entrate,
        nome_foglio="Entrate"
    )

    # FORMATTAZIONE DATA
    df_entrate[design["COL_ENTRATE_DATA"]] = pd.to_datetime(df_entrate[design["COL_ENTRATE_DATA"]],errors="coerce",dayfirst=True)

    df_entrate.insert(0, design["COL_ENTRATE_MESE"], int(mese_numb))

    df_entrate.sort_values(by=design["COL_ENTRATE_DATA"], inplace=True)

    return df_entrate


# CONTROLLI
def stampa_duplicati(df: pd.DataFrame, nome_tabella: str):
    duplicati = df[df.duplicated(keep=False)]

    if not duplicati.empty:
        print(f"\n\t-!- DUPLICATI TROVATI NELLE {nome_tabella.upper()}:")
        print("\t" +duplicati.to_string(index=False).replace("\n", "\n\t"))
    else:
        print(f"\n\t- {nome_tabella.upper()} senza duplicati")

def stampa_spese_altro(df_spese: pd.DataFrame, design: dict):
    spese_altro = df_spese[
        df_spese[design["COL_SPESE_CATEGORIA"]].astype(str).str.strip().str.lower() == "altro"
    ]

    if not spese_altro.empty:
        print('\n\t- SPESSE CON CATEGORIA "ALTRO":')
        print("\t" + spese_altro.sort_values(by=design["COL_SPESE_DATA"]).to_string(index=False).replace("\n","\n\t"))
    else:
        print('Nessuna spesa con categoria "Altro".')

# ------------------------------------- FUNZIONE PRINCIPALE -------------------------------------
def processa_mese(
        anno: str, 
        mese_numb: str,
        design: dict,
        structure: dict,
        colonne_app: dict,
        flag_blocca_se_input_manca: bool = True, 
        flag_sovrascrivi_output: bool = False,
        flag_stampa_percorsi: bool = False,
        flag_stampa_duplicati: bool = False,
        flag_processa_tutti_i_mesi: bool = False,
        flag_stampa_spese_altro: bool = False):
    
    percorsi = prepara_percorsi(
        anno=anno,
        mese_numb=mese_numb,
        structure=structure,
        flag_blocca_se_input_manca=flag_blocca_se_input_manca,
        flag_sovrascrivi_output=flag_sovrascrivi_output
    )

    
    if percorsi is None:
        return
    
    if flag_stampa_percorsi and not flag_processa_tutti_i_mesi:
        print("\nPercorsi dei file:")
        print(f"\tInput:\t{percorsi['input_file']}")
        print(f"\tOutput:\t{percorsi['output_file']}")

    df_spese = prepara_spese(
        input_file=percorsi["input_file"],
        additional_rows_csv=percorsi["additional_rows_csv"],
        anno=anno,
        mese_numb=mese_numb,
        design=design,
        colonne_app_spese=colonne_app["COLONNE_SPESE"]
    )

    df_entrate = prepara_entrate(
        input_file=percorsi["input_file"],
        mese_numb=mese_numb,
        design=design,
        colonne_app_entrate=colonne_app["COLONNE_ENTRATE"]
    )

    if flag_stampa_duplicati and not flag_processa_tutti_i_mesi:
        stampa_duplicati(df_spese, "Spese")
        stampa_duplicati(df_entrate, "Entrate")
    
    if flag_stampa_spese_altro and not flag_processa_tutti_i_mesi: 
        stampa_spese_altro(df_spese, design)

    # Formattazione finale per output Excel
    
    df_spese = formatta_dataframe_output(df_spese, colonna_data=design["COL_SPESE_DATA"], colonna_importo=design["COL_SPESE_IMPORTO"])
    df_entrate = formatta_dataframe_output(df_entrate, colonna_data=design["COL_ENTRATE_DATA"], colonna_importo=design["COL_ENTRATE_IMPORTO"])
    
    
    # Esportazione
    esporta_excel(
        df_spese=df_spese,
        df_entrate=df_entrate,
        output_file=percorsi["output_file"]
    )
