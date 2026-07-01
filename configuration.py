#FORMATO DEI NOMI DEI FILE DI INPUT E OUTPUT
from MAIN import COL_CATEGORIA, COL_DATA, COL_ENTRATE_NOTE, COL_IMPORTO, COL_SPESE_NOTE


def NOME_INPUT(YYYY, MM): return f"app_{YYYY}_{MM}.xlsx"
def NOME_OUTPUT(YYYY, MM): return f"p_{YYYY}_{MM}.xlsx"


# ------------------------------------- CONFIGURAZIONE -------------------------------------

STRUTTURA_DATI = {
    "MAIN_FOLDER":      "Dati",
    "APP_FILE_FOLDER":  "TabelleApp",
    "PROCESSED_FOLDER": "TabelleProcessed",
    "CSV_ADD_ROWS":     "additional_rows.csv",
}

# ----------------------------------------- DESIGN -----------------------------------------

DESIGN = {
    "COL_SPESE_DATA":           "Data",
    "COL_SPESE_CATEGORIA":      "Categoria",
    "COL_SPESE_IMPORTO":        "Importo",
    "COL_SPESE_NOTE":           "Note",
    
    "COL_ENTRATE_DATA":         "Data",
    "COL_ENTRATE_CATEGORIA":    "Categoria",
    "COL_ENTRATE_MESE":         "Mese",
    "COL_ENTRATE_IMPORTO":      "Importo",
    "COL_ENTRATE_NOTE":         "Note"
}

NOMI_COLONNE_APP = {
    "COLONNE_SPESE": {
        "COL_SPESE_DATA":           "Data e ora",
        "COL_SPESE_CATEGORIA":      "Categoria",
        "COL_SPESE_IMPORTO":        "Importo in valuta del conto",
        "COL_SPESE_NOTE":           "Commento",
    },
    "COLONNE_ENTRATE": {
        "COL_ENTRATE_DATA":         "Data e ora",
        "COL_ENTRATE_CATEGORIA":    "Categoria",
        "COL_ENTRATE_IMPORTO":      "Importo in valuta del conto",
        "COL_ENTRATE_NOTE":         "Commento",
    }
}


PROCESSA_TUTTI_I_MESI = 0
# 0 = processa solo ANNO / MESE_NUMB
# 1 = processa tutti i mesi in TUTTI_I_MESI

# ----- Opzioni -----
SOVRASCRIVI_OUTPUT = 1
# 0 = blocca se il file di output esiste già
# 1 = ignora il controllo e sovrascrive il file

SALTA_SE_INPUT_MANCANTE = 0
# 0 = blocca se il file di input non esiste
# 1 = salta il file se non esiste

STAMPA_DUPLICATI    = 1
STAMPA_SPESE_ALTRO  = 1
STAMPA_PERCORSI     = 0



