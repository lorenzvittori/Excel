from openpyxl import load_workbook

input_file = r'C:\Users\lvitt\OneDrive\Documenti\GiuHub Local Repository\FLUSSO_SpeseEntrate\Dati\TabelleApp\p_Dicembre25.xlsx'

wb = load_workbook(filename=input_file, data_only=True)
sheet = wb['Spese']  # o sheet = wb.active

cella = sheet['D3']
print(f"Valore in D3: {cella.value}")
print(f"Tipo della cella in D3: {cella.data_type}")