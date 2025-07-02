import pandas as pd

# ------------------------------ CONFIGURAZIONE ------------------------------

MeseAttuale = 'Giugno'
AnnoAttuale = '2025'



AnnoAttualeShort = AnnoAttuale[2:]

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

# Percorsi dei file
folder_path = r'C:\Users\lvitt\OneDrive\Desktop\Personale\SPESE-ENTRATE'


default_input = fr'{folder_path}\{AnnoAttuale}\{MeseAttuale} {AnnoAttualeShort} - App.xlsx'
default_output = fr'{folder_path}\{AnnoAttuale}\{MeseAttuale} {AnnoAttualeShort} - Processed.xlsx'


# Opzionali input/output personalizzati
customize_input = r'Dati\2025_07_02_11_21_49_685694.xlsx'
customize_output = fr'Dati\p_{MeseAttuale}{AnnoAttuale}.xlsx'

input_file = default_input if customize_input == '' else customize_input
output_file = default_output if customize_output == '' else customize_output

# ------------------------------ FUNZIONI UTILI ------------------------------

def DAY_TO_DATA(giorno) -> str:
    try:
        giorno_str = str(int(giorno)).zfill(2)
        return f"{giorno_str}/{DizMesi[MeseAttuale]}/{AnnoAttuale}"
    except (ValueError, TypeError):
        return 'INVALID_DATE'

# ------------------------------ LETTURA FILE PRINCIPALE ------------------------------

df = pd.read_excel(input_file, sheet_name='Spese', skiprows=1, header=0)

# Rimuovo colonne inutili
colonne_da_rimuovere = [2, 3, 4, 6, 7, 8, 9]
df.drop(df.columns[colonne_da_rimuovere], axis=1, inplace=True)

# Rinomino intestazioni
df.rename(columns={
    df.columns[0]: 'Data',
    df.columns[1]: 'Categoria',
    df.columns[2]: 'Importo',
    df.columns[3]: 'Commento'
}, inplace=True)

# Formattazione data
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')

# ------------------------------ LETTURA RIGHE AGGIUNTIVE DA CSV ------------------------------

df_nuove_righe_raw = pd.read_csv('added_rows.csv')

# Genera la colonna "Data" formattata da "GiornoData"
df_nuove_righe_raw['Data'] = df_nuove_righe_raw['GiornoData'].apply(DAY_TO_DATA)

# Preparo il DataFrame nello stesso formato
nuove_righe = df_nuove_righe_raw[['Data', 'Categoria', 'Importo']].copy()
nuove_righe['Commento'] = ''

# ------------------------------ UNIONE E PULIZIA ------------------------------

df = pd.concat([df, nuove_righe], ignore_index=True)
df.insert(1, 'Gruppo', '')                # Aggiunge colonna "Gruppo" vuota
df.sort_values(by='Data', inplace=True)  # Ordina per Data
df.drop_duplicates(inplace=True)         # Rimuove duplicati

# ------------------------------ ESPORTAZIONE ------------------------------

df.to_excel(output_file, index=False)
