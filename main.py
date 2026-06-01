import pandas as pd
from pathlib import Path

# ------------------------------ CONFIGURAZIONE ------------------------------

DIZ_MESI = {
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

# ------------------------------ MODIFICABILE ------------------------------

MESE_ATTUALE = "Maggio"
ANNO_ATTUALE = "2026"

# ------------------------------ SETUP PERCORSI ------------------------------

ROOT_DIR = Path(__file__).resolve().parent

DATI_DIR = ROOT_DIR / "Dati"
INPUT_DIR = DATI_DIR / "TabelleApp"
OUTPUT_DIR = DATI_DIR / "TabelleProcessed"

ANNO_SHORT = ANNO_ATTUALE[-2:]

input_file = INPUT_DIR / f"app_{MESE_ATTUALE}{ANNO_SHORT}.xlsx"
output_file = OUTPUT_DIR / f"p_{MESE_ATTUALE}{ANNO_SHORT}.xlsx"
added_rows_file = ROOT_DIR / "added_rows.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not input_file.exists():
    raise FileNotFoundError(
        f"File Excel non trovato:\n{input_file}\n\n"
        f"Controlla che esista questo file:\n"
        f"app_{MESE_ATTUALE}{ANNO_SHORT}.xlsx\n\n"
        f"Dentro la cartella:\n{INPUT_DIR}"
    )

if not added_rows_file.exists():
    raise FileNotFoundError(
        f"File CSV non trovato:\n{added_rows_file}\n\n"
        f"Controlla che added_rows.csv sia dentro:\n{ROOT_DIR}"
    )

print(f"Input Excel: {input_file}")
print(f"Input CSV:   {added_rows_file}")
print(f"Output:      {output_file}")

# ------------------------------ FUNZIONI ------------------------------

def day_to_data(giorno) -> str:
    try:
        giorno_str = str(int(giorno)).zfill(2)
        return f"{giorno_str}/{DIZ_MESI[MESE_ATTUALE]}/{ANNO_ATTUALE}"
    except (ValueError, TypeError):
        return "INVALID_DATE"


def format_importo(value):
    if pd.isnull(value):
        return ""

    try:
        return f"{float(value):.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return value


# ===================================================== LETTURA FILE EXCEL =====================

# -------------------------------------------------- SPESE --------------------------------------------------

df_spese = pd.read_excel(
    input_file,
    sheet_name="Spese",
    skiprows=1,
    header=0
)

colonne_da_rimuovere = [2, 4, 5, 6, 7]
df_spese.drop(df_spese.columns[colonne_da_rimuovere], axis=1, inplace=True)

df_spese.rename(columns={
    df_spese.columns[0]: "Data",
    df_spese.columns[1]: "Categoria",
    df_spese.columns[2]: "Importo",
    df_spese.columns[3]: "Commento"
}, inplace=True)

df_spese["Data"] = pd.to_datetime(
    df_spese["Data"],
    errors="coerce",
    dayfirst=True
)

df_spese_nuove_righe_raw = pd.read_csv(added_rows_file)

df_spese_nuove_righe_raw["Data"] = df_spese_nuove_righe_raw["GiornoData"].apply(day_to_data)

df_spese_nuove_righe_raw["Data"] = pd.to_datetime(
    df_spese_nuove_righe_raw["Data"],
    errors="coerce",
    dayfirst=True
)

nuove_righe = df_spese_nuove_righe_raw[["Data", "Categoria", "Importo"]].copy()
nuove_righe["Commento"] = ""

df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)

df_spese.sort_values(by="Data", inplace=True)

duplicati_spese = df_spese[df_spese.duplicated(keep=False)]

if not duplicati_spese.empty:
    print("\n!!! DUPLICATI TROVATI NELLE SPESE !!!")
    print(duplicati_spese.sort_values(by=df_spese.columns.tolist()))


# -------------------------------------------------- ENTRATE --------------------------------------------------

df_entrate = pd.read_excel(
    input_file,
    sheet_name="Entrate",
    skiprows=1,
    header=0
)

colonne_da_rimuovere = [2, 4, 5, 6, 7]
df_entrate.drop(df_entrate.columns[colonne_da_rimuovere], axis=1, inplace=True)

df_entrate.rename(columns={
    df_entrate.columns[0]: "Data",
    df_entrate.columns[1]: "Categoria",
    df_entrate.columns[2]: "Importo",
    df_entrate.columns[3]: "Note"
}, inplace=True)

df_entrate["Data"] = pd.to_datetime(
    df_entrate["Data"],
    errors="coerce",
    dayfirst=True
)

df_entrate.insert(0, "Mese", int(DIZ_MESI[MESE_ATTUALE]))

df_entrate.sort_values(by="Data", inplace=True)

duplicati_entrate = df_entrate[df_entrate.duplicated(keep=False)]

if not duplicati_entrate.empty:
    print("\n!!! DUPLICATI TROVATI NELLE ENTRATE !!!")
    print(duplicati_entrate.sort_values(by=df_entrate.columns.tolist()))


# -------------------------------------------------- FORMAT DATA --------------------------------------------------

df_spese["Data"] = df_spese["Data"].apply(
    lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
)

df_entrate["Data"] = df_entrate["Data"].apply(
    lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else ""
)


# -------------------------------------------------- CONVERSIONE IMPORTO --------------------------------------------------

df_spese["Importo"] = df_spese["Importo"].apply(format_importo)
df_entrate["Importo"] = df_entrate["Importo"].apply(format_importo)


# ------------------------------ ESPORTAZIONE ------------------------------

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_spese.to_excel(writer, sheet_name="Spese", index=False)
    df_entrate.to_excel(writer, sheet_name="Entrate", index=False)

print(f"\nFile salvato correttamente in:\n{output_file}")