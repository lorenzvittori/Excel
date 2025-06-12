import pandas as pd

MeseAttuale = 'Maggio'
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


# ------------------------------ IMPORT ------------------------------

# File di import
input_file = r'C:\Users\lvitt\OneDrive\Desktop\Personale\SPESE-ENTRATE' + '\\' + AnnoAttuale + '\\' + MeseAttuale + ' ' + AnnoAttualeShort + ' - App' + '.xlsx'

# Creazione DataFrame di manipolazione
df = pd.read_excel(input_file, sheet_name='Spese',skiprows=1, header = 0)

# ------------------------------ MANIPOLAZIONE ------------------------------

# Rimozione Colonne inutili
colonne_da_rimuovere = [2, 3, 4, 6, 7, 8, 9]  # Indici delle colonne da rimuovere
df.drop(df.columns[colonne_da_rimuovere], axis=1, inplace=True)

# Rinomina dell'intestazione
df.rename(columns={df.columns[0]: 'Data'}, inplace=True)
df.rename(columns={df.columns[1]: 'Categoria'}, inplace=True)
df.rename(columns={df.columns[2]: 'Importo'}, inplace=True)
df.rename(columns={df.columns[3]: 'Commento'}, inplace=True)


# ------------------------------ RIFORMATIZZAZIONE ------------------------------

# Cambia il formato della colonna "Data"
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
# Riformatta la colonna "Data" nel formato dd/mm/yyyy
df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')



# ------------------------------ RIGHE STANDARD ------------------------------
# ------------------------------ FUNZIONI ------------------------------
def genera_data_formattata(giorno: str) -> str:
    return f"{giorno.zfill(2)}/{DizMesi[MeseAttuale]}/{AnnoAttuale}"


# ------------------------------ RIGHE STANDARD ------------------------------
nuove_righe_array = [
    {
        'GiornoData': '04',
        'Categoria': 'Commissione CC',
        'Importo': 1.6
    },
    {
        'GiornoData': '05',
        'Categoria': 'Rata PDR',
        'Importo': 50
    },
    {
        'GiornoData': '11',
        'Categoria': 'Abbonamento Telefono',
        'Importo': 7.99
    },
    {
        'GiornoData': '20',
        'Categoria': 'Spotify',
        'Importo': 3
    },
]

# Genera il DataFrame da nuove_righe_array
nuove_righe = pd.DataFrame([
    {
        'Data': genera_data_formattata(riga['GiornoData']),
        'Categoria': riga['Categoria'],
        'Importo': riga['Importo'],
        'Commento': ''
    }
    for riga in nuove_righe_array
])

# Unione al DataFrame principale
df = pd.concat([df, nuove_righe], ignore_index=True)


# ------------------------------ MANIPOLAZIONE ------------------------------

# Aggiungo la colonna Gruppo vuota
df.insert(1, 'Gruppo', '')

# Ordino i dati per data
df.sort_values(by='Data', inplace=True)

# Rimuovi eventuali duplicati
df.drop_duplicates(inplace=True)



# ------------------------------ EXPORT ------------------------------

output_file = r'C:\Users\lvitt\OneDrive\Desktop\Personale\SPESE-ENTRATE' + '\\' + AnnoAttuale + '\\' + MeseAttuale + ' ' + AnnoAttualeShort + ' - Processed' + '.xlsx'

df.to_excel(output_file, index=False)






