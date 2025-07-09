import pandas as pd

# ------------------------------ CONFIGURAZIONE ------------------------------
customize_input = ''
customize_output = ''

DizMesi = {
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

#-------------------------------- v MODIFICABILE  v---------------------------------
MeseAttuale = 'Giugno'
AnnoAttuale = '2025'


# Percorsi dei file
folder_path = r'C:\Users\lvitt\OneDrive\Desktop\Personale\SPESE-ENTRATE'


# Opzionali input/output personalizzati
#customize_input = r'Dati\2025_07_02_11_21_49_685694.xlsx'
#customize_output = fr'Dati\p_{MeseAttuale}{AnnoAttuale}.xlsx'

#--------------------------------^ MODIFICABILE ^---------------------------------




# ---- SET UP --------
AnnoAttualeShort = AnnoAttuale[2:]

default_input = fr'{folder_path}\{AnnoAttuale}\{MeseAttuale} {AnnoAttualeShort} - App.xlsx'
default_output = fr'{folder_path}\{AnnoAttuale}\{MeseAttuale} {AnnoAttualeShort} - Processed.xlsx'


input_file = default_input if customize_input == '' else customize_input
output_file = default_output if customize_output == '' else customize_output

#-------------------------------------------------- SPESE --------------------------------------------------

# ---- LETTURA FILE PRINCIPALE ----

df_spese = pd.read_excel(input_file, sheet_name='Spese', skiprows=1, header=0)

# Rimuovo colonne inutili
colonne_da_rimuovere = [2, 3, 4, 6, 7, 8, 9]
df_spese.drop(df_spese.columns[colonne_da_rimuovere], axis=1, inplace=True)

# Rinomino intestazioni
df_spese.rename(columns={
    df_spese.columns[0]: 'Data',
    df_spese.columns[1]: 'Categoria',
    df_spese.columns[2]: 'Importo',
    df_spese.columns[3]: 'Commento'
}, inplace=True)


# Formattazione data
df_spese['Data'] = pd.to_datetime(df_spese['Data'], errors='coerce')
df_spese['Data'] = df_spese['Data'].dt.strftime('%d/%m/%Y')

# ---- LETTURA RIGHE AGGIUNTIVE DA CSV ----

def DAY_TO_DATA(giorno) -> str:
    try:
        giorno_str = str(int(giorno)).zfill(2)
        return f"{giorno_str}/{DizMesi[MeseAttuale]}/{AnnoAttuale}"
    except (ValueError, TypeError):
        return 'INVALID_DATE'

df_spese_nuove_righe_raw = pd.read_csv('added_rows.csv')

# Genera la colonna "Data" formattata da "GiornoData"
df_spese_nuove_righe_raw['Data'] = df_spese_nuove_righe_raw['GiornoData'].apply(DAY_TO_DATA)

# Preparo il DataFrame nello stesso formato
nuove_righe = df_spese_nuove_righe_raw[['Data','Categoria', 'Importo']].copy()
nuove_righe['Commento'] = ''

# ---- UNIONE E PULIZIA ----

df_spese = pd.concat([df_spese, nuove_righe], ignore_index=True)
df_spese.insert(1, 'Gruppo', '')               # Aggiunge colonna "Gruppo" vuota
df_spese.sort_values(by='Data', inplace=True)  # Ordina per Data


duplicati = df_spese.duplicated().any()

# Se ci sono duplicati, restituisce una stringa
if duplicati:
    print("Ci sono duplicati nelle SPESE" )

#----Aggiunta del gruppo ----
df_spese.reset_index(drop=True, inplace=True)  # Assicurati che gli indici siano 0,1,2,...

def crea_formula_excel(riga_idx):
    # Riga Excel parte da 2 (per via dell'header), quindi +2 rispetto all'indice 0-based di pandas
    excel_row = riga_idx + 2
    return f'=CERCA.VERT(C{excel_row};Categorie!$A$2:$B$10003;2;FALSO)'

df_spese['Gruppo'] = [crea_formula_excel(i) for i in range(len(df_spese))]



#-------------------------------------------------- ENTRATE --------------------------------------------------

# ---- LETTURA FILE PRINCIPALE ----

df_entrate = pd.read_excel(input_file, sheet_name='Entrate', skiprows=1, header=0)

# Rimuovo colonne inutili
colonne_da_rimuovere = [2, 3, 4, 6, 7, 8, 9] #prima colonna -> indice 0
df_entrate.drop(df_entrate.columns[colonne_da_rimuovere], axis=1, inplace=True)

# Rinomino intestazioni
df_entrate.rename(columns={
    df_entrate.columns[0]: 'Data',
    df_entrate.columns[1]: 'Categoria',
    df_entrate.columns[2]: 'Importo',
    df_entrate.columns[3]: 'Note'
}, inplace=True)


# Formattazione data
df_entrate['Data'] = pd.to_datetime(df_entrate['Data'], errors='coerce')
df_entrate['Data'] = df_entrate['Data'].dt.strftime('%d/%m/%Y')


# ---- UNIONE E PULIZIA ----

df_entrate.insert(0, 'Mese', f'{int(DizMesi[MeseAttuale])}')
df_entrate.sort_values(by='Data', inplace=True)  # Ordina per Data



duplicati = df_entrate.duplicated().any()

# Se ci sono duplicati, restituisce una stringa
if duplicati:
    print("Ci sono duplicati nelle ENTRATE" )


# ------------------------------ ESPORTAZIONE ------------------------------

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_spese.to_excel(writer, sheet_name='Spese', index=False)
    df_entrate.to_excel(writer, sheet_name='Entrate', index=False)
