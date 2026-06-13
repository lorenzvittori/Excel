import pandas as pd
from pathlib import Path


# ------------------------------ CONFIGURAZIONE ------------------------------

SOVRASCRIVI_OUTPUT = 0
# 0 = blocca se il file di output esiste già
# 1 = ignora il controllo e sovrascrive il file


mesi_da_processare = [ ("2026", "05") ]


PROCESSA_TUTTI_I_MESI = 0
# 0 = processa solo ANNO / MESE_NUMB
# 1 = processa tutti i mesi in TUTTI_I_MESI


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
    "Dicembre": "12",
}

DIZ_NUMB_TO_MESE = {v: k for k, v in DIZ_MESE_TO_NUMB.items()}

COLONNE_SPESE = {
    "Data e ora": "Data",
    "Categoria": "Categoria",
    "Importo in valuta del conto": "Importo",
    "Commento": "Note",
}

COLONNE_ENTRATE = {
    "Data e ora": "Data",
    "Categoria": "Categoria",
    "Importo in valuta del conto": "Importo",
    "Commento": "Note",
}


COL_SPESE_DATA = COLONNE_SPESE["Data e ora"]
COL_SPESE_CATEGORIA = COLONNE_SPESE["Categoria"]
COL_SPESE_IMPORTO = COLONNE_SPESE["Importo in valuta del conto"]
COL_SPESE_NOTE = COLONNE_SPESE["Commento"]

COL_ENTRATE_DATA = COLONNE_ENTRATE["Data e ora"]
COL_ENTRATE_CATEGORIA = COLONNE_ENTRATE["Categoria"]
COL_ENTRATE_IMPORTO = COLONNE_ENTRATE["Importo in valuta del conto"]
COL_ENTRATE_NOTE = COLONNE_ENTRATE["Commento"]

COL_MESE = "Mese"

def prepara_percorsi( anno: str,mese_numb: str, blocca_se_input_manca: bool = True, sovrascrivi_output: bool = False ) -> dict | None:
    root_dir = Path(__file__).resolve().parent
    dati_dir = root_dir / "Dati"
    input_dir = dati_dir / "TabelleApp"
    output_dir = dati_dir / "TabelleProcessed"

    input_file = input_dir / f"app_{anno}_{mese_numb}.xlsx"
    output_file = output_dir / f"p_{anno}_{mese_numb}.xlsx"
    added_rows_file = root_dir / "added_rows.csv"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print("\n!!! FILE EXCEL NON TROVATO !!!")
        print(input_file)

        if blocca_se_input_manca:
            raise SystemExit

        print(f"Mese {anno}-{mese_numb} saltato.")
        return None

    if not added_rows_file.exists():
        print("\n!!! FILE CSV NON TROVATO !!!")
        print(added_rows_file)
        raise SystemExit

    if output_file.exists() and not sovrascrivi_output:
        print("\n!!! FILE DI OUTPUT GIA' ESISTENTE !!!")
        print(output_file)
        print("\nPer evitare sovrascritture, elimina o rinomina il file esistente prima di rieseguire lo script.")
        print("Oppure imposta SOVRASCRIVI_OUTPUT = 1.")

        raise SystemExit

    return {
        "root_dir": root_dir,
        "input_file": input_file,
        "output_file": output_file,
        "added_rows_file": added_rows_file,
    }

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

def converti_colonna_data(df: pd.DataFrame, colonna: str = "Data") -> pd.DataFrame:
    df = df.copy()

    df[colonna] = pd.to_datetime(
        df[colonna],
        errors="coerce",
        dayfirst=True
    )

    return df

def format_importo(value):
    if pd.isnull(value):
        return ""

    try:
        return f"{float(value):.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return value

def formatta_dataframe_output(
    df: pd.DataFrame,
    colonna_data: str,
    colonna_importo: str
) -> pd.DataFrame:
    df = df.copy()

    df[colonna_data] = df[colonna_data].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
    )

    df[colonna_importo] = df[colonna_importo].apply(format_importo)

    return df

def esporta_excel(
    df_spese: pd.DataFrame,
    df_entrate: pd.DataFrame,
    output_file: Path
):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_spese.to_excel(writer, sheet_name="Spese", index=False)
        df_entrate.to_excel(writer, sheet_name="Entrate", index=False)

    print(f"\nFile salvato correttamente in:\n{output_file}")
    

    
def leggi_spese(input_file: Path) -> pd.DataFrame:
    df_spese = pd.read_excel(
        input_file,
        sheet_name="Spese",
        skiprows=1,
        header=0
    )

    df_spese = seleziona_e_rinomina_colonne(
        df=df_spese,
        mappa_colonne=COLONNE_SPESE,
        nome_foglio="Spese"
    )

    df_spese = converti_colonna_data(df_spese, COL_SPESE_DATA)

    return df_spese

def day_to_data(giorno, anno: str, mese_numb: str) -> str:
    try:
        giorno_str = str(int(giorno)).zfill(2)
        return f"{giorno_str}/{mese_numb}/{anno}"
    except (ValueError, TypeError):
        return "INVALID_DATE"

def aggiungi_righe_spese(
    df_spese: pd.DataFrame,
    added_rows_file: Path,
    anno: str,
    mese_numb: str
) -> pd.DataFrame:
    df_nuove_righe_raw = pd.read_csv(added_rows_file)

    df_nuove_righe_raw[COL_SPESE_DATA] = df_nuove_righe_raw["GiornoData"].apply(
        lambda giorno: day_to_data(giorno, anno, mese_numb)
    )

    df_nuove_righe_raw = converti_colonna_data(df_nuove_righe_raw, COL_SPESE_DATA)

    nuove_righe = df_nuove_righe_raw[
        [COL_SPESE_DATA, COL_SPESE_CATEGORIA, COL_SPESE_IMPORTO]
    ].copy()

    nuove_righe[COL_SPESE_NOTE] = ""

    df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)

    df_spese.sort_values(by=COL_SPESE_DATA, inplace=True)

    return df_spese


# ENTRATE
def leggi_entrate(input_file: Path) -> pd.DataFrame:
    df_entrate = pd.read_excel(
        input_file,
        sheet_name="Entrate",
        skiprows=1,
        header=0
    )

    df_entrate = seleziona_e_rinomina_colonne(
        df=df_entrate,
        mappa_colonne=COLONNE_ENTRATE,
        nome_foglio="Entrate"
    )

    df_entrate = converti_colonna_data(df_entrate, COL_ENTRATE_DATA)

    return df_entrate

def prepara_entrate(input_file: Path, mese_numb: str) -> pd.DataFrame:
    df_entrate = leggi_entrate(input_file)

    df_entrate.insert(0, COL_MESE, int(mese_numb))

    df_entrate.sort_values(by=COL_ENTRATE_DATA, inplace=True)

    return df_entrate


#CONTROLLI
def stampa_duplicati(df: pd.DataFrame, nome_tabella: str):
    duplicati = df[df.duplicated(keep=False)]

    if not duplicati.empty:
        print(f"\n!!! DUPLICATI TROVATI NELLE {nome_tabella.upper()} !!!")
        print(duplicati.sort_values(by=df.columns.tolist()))

def stampa_spese_altro(df_spese: pd.DataFrame):
    spese_altro = df_spese[
        df_spese[COL_SPESE_CATEGORIA].astype(str).str.strip().str.lower() == "altro"
    ]

    if not spese_altro.empty:
        print('\n!!! SPESE CON CATEGORIA "ALTRO" !!!')
        print(spese_altro.sort_values(by=COL_SPESE_DATA))
    else:
        print('\nNessuna spesa con categoria "Altro".')

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

    print(f"Input Excel: {percorsi['input_file']}")
    print(f"Input CSV:   {percorsi['added_rows_file']}")
    print(f"Output:      {percorsi['output_file']}")

    df_spese = leggi_spese(percorsi["input_file"])

    df_spese = aggiungi_righe_spese(
        df_spese=df_spese,
        added_rows_file=percorsi["added_rows_file"],
        anno=anno,
        mese_numb=mese_numb
    )

    df_entrate = prepara_entrate(
        input_file=percorsi["input_file"],
        mese_numb=mese_numb
    )

    stampa_duplicati(df_spese, "Spese")
    stampa_spese_altro(df_spese)

    stampa_duplicati(df_entrate, "Entrate")

    df_spese = formatta_dataframe_output(
        df_spese,
        colonna_data=COL_SPESE_DATA,
        colonna_importo=COL_SPESE_IMPORTO
    )

    df_entrate = formatta_dataframe_output(
        df_entrate,
        colonna_data=COL_ENTRATE_DATA,
        colonna_importo=COL_ENTRATE_IMPORTO
    )

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
            print("=" * 80)

            processa_mese(
                anno=anno,
                mese_numb=mese_numb,
                blocca_se_input_manca=False,
                sovrascrivi_output=True
            )

    else:
        for anno, mese_numb in mesi_da_processare:
            print("\n" + "=" * 80)
            print(f"PROCESSO {anno}-{mese_numb}")
            print("=" * 80)

            processa_mese(
                anno=anno,
                mese_numb=mese_numb,
                blocca_se_input_manca=True,
                sovrascrivi_output=bool(SOVRASCRIVI_OUTPUT)
            )