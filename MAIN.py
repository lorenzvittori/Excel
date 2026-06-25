import pandas as pd
from pathlib import Path


# ------------------------------------- CONFIGURAZIONE -------------------------------------
# ----- Mesi da processare
mesi_da_processare = {"2026": ["05"]}

PROCESSA_TUTTI_I_MESI = 0
# 0 = processa solo ANNO / MESE_NUMB
# 1 = processa tutti i mesi in TUTTI_I_MESI

# ----- Opzioni -----
SOVRASCRIVI_OUTPUT = 1
# 0 = blocca se il file di output esiste già
# 1 = ignora il controllo e sovrascrive il file

STAMPA_DUPLICATI    = 1
STAMPA_SPESE_ALTRO  = 1
STAMPA_PERCORSI     = 0

# ----------------------------------------- DESIGN -----------------------------------------
COL_DATA = "Data"
COL_CATEGORIA = "Categoria"
COL_IMPORTO = "Importo"
COL_SPESE_NOTE = "Note"
COL_ENTRATE_NOTE = "Note"
COL_ENTRATE_MESE = "Mese"

MAIN_FOLDER = "Dati"
FILEAPP_FOLDER = "TabelleApp"
PROCESSED_FOLDER = "TabelleProcessed"

CSV_ADD_ROWS = "additional_rows.csv"

#FOORMATO DEI NOMI DEI FILE DI INPUT E OUTPUT
def NOME_INPUT(YYYY, MM): return f"app_{YYYY}_{MM}.xlsx"
def NOME_OUTPUT(YYYY, MM): return f"p_{YYYY}_{MM}.xlsx"


# ------------------------------ COSTANTI ------------------------------
TUTTI_I_MESI = [
    (str(anno), str(mese).zfill(2))
    for anno in range(2024, 2030)
    for mese in range(1, 13)
]

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

COLONNE_SPESE = {
    "Data e ora": COL_DATA,
    "Categoria": COL_CATEGORIA,
    "Importo in valuta del conto": COL_IMPORTO,
    "Commento": COL_SPESE_NOTE,
}

COLONNE_ENTRATE = {
    "Data e ora": COL_DATA,
    "Categoria": COL_CATEGORIA,
    "Importo in valuta del conto": COL_IMPORTO,
    "Commento": COL_ENTRATE_NOTE,
}

# ------------------------------ FUNZIONI ------------------------------
# STRUTTURALI
def prepara_percorsi( anno: str,mese_numb: str, blocca_se_input_manca: bool = True, sovrascrivi_output: bool = False ) -> dict | None:
    root_dir = Path(__file__).resolve().parent
    dati_dir = root_dir / MAIN_FOLDER
    input_dir = dati_dir / FILEAPP_FOLDER
    output_dir = dati_dir / PROCESSED_FOLDER

    input_file = input_dir / NOME_INPUT(anno, mese_numb)
    output_file = output_dir / NOME_OUTPUT(anno, mese_numb)
    additional_rows_csv = root_dir / CSV_ADD_ROWS

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"\t-!- FILE {NOME_INPUT(anno, mese_numb)} NON ESISTENTE")

        if blocca_se_input_manca:
            print("=" * 80)
            print("\nP R O C E S S O   T E R M I N A T O")
            raise SystemExit

        else:
            print(f"\t - FILE {NOME_INPUT(anno, mese_numb)} SALTATO.")
            return None

    if not additional_rows_csv.exists():
        print("\t-!- FILE CSV NON TROVATO", end="\t")
        print(f"...\{CSV_ADD_ROWS}")
        raise SystemExit

    if output_file.exists():
        if not sovrascrivi_output:
            print(f"\t-!- FILE {NOME_OUTPUT(anno, mese_numb)} GIA' ESISTENTE -> il processo si blocca")
            print("=" * 80)
            print("\nP R O C E S S O   T E R M I N A T O")
            raise SystemExit
        else:
            print(f"\t-!- FILE {NOME_OUTPUT(anno, mese_numb)} GIA' ESISTENTE -> file sovrascritto")
            
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
def aggiungi_righe_spese(df_spese: pd.DataFrame, additional_rows_csv: Path, anno: str, mese_numb: str) -> pd.DataFrame:
    df_nuove_righe_raw = pd.read_csv(additional_rows_csv)

    df_nuove_righe_raw[COL_DATA] = df_nuove_righe_raw["GiornoData"].apply(
        lambda giorno: f"{str(int(giorno)).zfill(2)}/{mese_numb}/{anno}"
    )
    
    df_nuove_righe_raw[COL_DATA] = pd.to_datetime(
        df_nuove_righe_raw[COL_DATA],
        errors="coerce",
        dayfirst=True
    )

    nuove_righe = df_nuove_righe_raw[
        [COL_DATA, COL_CATEGORIA, COL_IMPORTO]
    ].copy()

    nuove_righe[COL_SPESE_NOTE] = ""

    df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)

    return df_spese

def prepara_spese(input_file: Path, additional_rows_csv: Path, anno: str, mese_numb: str) -> pd.DataFrame:
    #Lettura
    df_spese = pd.read_excel(
        input_file,
        sheet_name="Spese",
        skiprows=1,
        header=0
    )

    #Pulizia
    df_spese = seleziona_e_rinomina_colonne(
        df=df_spese,
        mappa_colonne=COLONNE_SPESE,
        nome_foglio="Spese"
    )

    #Aggiunta di nuove righe
    df_spese = aggiungi_righe_spese(
        df_spese=df_spese,
        additional_rows_csv=additional_rows_csv,
        anno=anno,
        mese_numb=mese_numb
    )
    
    # FORMATTAZIONE DATA
    df_spese[COL_DATA] = pd.to_datetime(df_spese[COL_DATA],errors="coerce",dayfirst=True)
    
    
    df_spese.sort_values(by=COL_DATA, inplace=True)
    
    return df_spese

# ENTRATE
def prepara_entrate(input_file: Path, mese_numb: str) -> pd.DataFrame:
    #Lettura 
    df_entrate = pd.read_excel(
        input_file,
        sheet_name="Entrate",
        skiprows=1,
        header=0
    )

    #Pulizia
    df_entrate = seleziona_e_rinomina_colonne(
        df=df_entrate,
        mappa_colonne=COLONNE_ENTRATE,
        nome_foglio="Entrate"
    )

    # FORMATTAZIONE DATA
    df_entrate[COL_DATA] = pd.to_datetime(df_entrate[COL_DATA],errors="coerce",dayfirst=True)

    df_entrate.insert(0, COL_ENTRATE_MESE, int(mese_numb))

    df_entrate.sort_values(by=COL_DATA, inplace=True)

    return df_entrate


# CONTROLLI
def stampa_duplicati(df: pd.DataFrame, nome_tabella: str):
    duplicati = df[df.duplicated(keep=False)]

    if not duplicati.empty:
        print(f"\n\t-!- DUPLICATI TROVATI NELLE {nome_tabella.upper()}:")
        print("\t" +duplicati.to_string(index=False).replace("\n", "\n\t"))
    else:
        print(f"\n\t- {nome_tabella.upper()} senza duplicati")

def stampa_spese_altro(df_spese: pd.DataFrame):
    spese_altro = df_spese[
        df_spese[COL_CATEGORIA].astype(str).str.strip().str.lower() == "altro"
    ]

    if not spese_altro.empty:
        print('\n\t- SPESSE CON CATEGORIA "ALTRO":')
        print("\t" + spese_altro.sort_values(by=COL_DATA).to_string(index=False).replace("\n","\n\t"))
    else:
        print('Nessuna spesa con categoria "Altro".')

# ------------------------------ FUNZIONE PRINCIPALE ------------------------------
def processa_mese(anno: str, mese_numb: str, blocca_se_input_manca: bool = True, sovrascrivi_output: bool = False):
    percorsi = prepara_percorsi(
        anno=anno,
        mese_numb=mese_numb,
        blocca_se_input_manca=blocca_se_input_manca,
        sovrascrivi_output=sovrascrivi_output
    )

    
    if percorsi is None:
        return
    
    if STAMPA_PERCORSI and not PROCESSA_TUTTI_I_MESI:
        print("\nPercorsi dei file:")
        print(f"\tInput:\t{percorsi['input_file']}")
        print(f"\tOutput:\t{percorsi['output_file']}")

    df_spese = prepara_spese(
        input_file=percorsi["input_file"],
        additional_rows_csv=percorsi["additional_rows_csv"],
        anno=anno,
        mese_numb=mese_numb
    )

    df_entrate = prepara_entrate(
        input_file=percorsi["input_file"],
        mese_numb=mese_numb
    )

    if STAMPA_DUPLICATI and not PROCESSA_TUTTI_I_MESI:
        stampa_duplicati(df_spese, "Spese")
        stampa_duplicati(df_entrate, "Entrate")
    
    if STAMPA_SPESE_ALTRO and not PROCESSA_TUTTI_I_MESI: 
        stampa_spese_altro(df_spese)

    # Formattazione finale per output Excel
    
    df_spese = formatta_dataframe_output(df_spese, colonna_data=COL_DATA, colonna_importo=COL_IMPORTO)
    df_entrate = formatta_dataframe_output(df_entrate, colonna_data=COL_DATA, colonna_importo=COL_IMPORTO)
    
    # Esportazione
    esporta_excel(
        df_spese=df_spese,
        df_entrate=df_entrate,
        output_file=percorsi["output_file"]
    )


# ------------------------------ AVVIO SCRIPT ------------------------------

if __name__ == "__main__":
    if PROCESSA_TUTTI_I_MESI == 1:
        for anno, mese_numb in TUTTI_I_MESI:
            print("\n" + "=" * 80)
            print(f"PROCESSO {anno}-{mese_numb}")

            processa_mese(
                anno=anno,
                mese_numb=mese_numb,
                blocca_se_input_manca=False,
                sovrascrivi_output=True
            )
            
            print("=" * 80)

    else:
        anni = mesi_da_processare.keys()
        for anno in anni:
            for mese_numb in mesi_da_processare[anno]:
                print("\n" + "=" * 80)
                print(f"PROCESSO {anno}-{mese_numb}")
                processa_mese(
                    anno=anno,
                    mese_numb=mese_numb,
                    blocca_se_input_manca=True,
                    sovrascrivi_output=bool(SOVRASCRIVI_OUTPUT)
                )
                
                print("=" * 80)