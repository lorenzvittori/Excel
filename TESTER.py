## NOME FILE: TESTER.py
"""
Script di verifica visiva per logger.py.
Nessuna dipendenza esterna (Dropbox, Google) - testa solo l'output del logger.
"""

import logger


def sezione(titolo: str) -> None:
    print("\n" + "#" * 60)
    print(f"# {titolo}")
    print("#" * 60 + "\n")


# ---------------------------------------------------------------
sezione("1. Messaggi semplici, senza fasi aperte")
logger.reset_fase()
logger.info_mex("Messaggio informativo semplice")
logger.warning_mex("Messaggio di warning semplice")
logger.error_mex("Messaggio di errore semplice")


# ---------------------------------------------------------------
sezione("2. Messaggi con dettaglio singolo (stringa)")
logger.reset_fase()
logger.info_mex("Connessione riuscita", dettaglio="Tempo impiegato: 0.4s")
logger.warning_mex("File già esistente", dettaglio="Verrà sovrascritto")
logger.error_mex("Download fallito", dettaglio="Timeout dopo 30s")


# ---------------------------------------------------------------
sezione("3. Messaggi con dettaglio multiplo (lista)")
logger.reset_fase()
logger.error_mex(
    corpo="Colonne mancanti nel foglio Spese",
    dettaglio=["Data e ora", "Categoria", "Importo in valuta del conto"]
)
logger.warning_mex(
    corpo="Duplicati trovati",
    dettaglio=["Riga 12: Cibo Fuori 20,00", "Riga 45: Cibo Fuori 20,00", "Riga 88: Alcool 8,50"]
)


# ---------------------------------------------------------------
sezione("4. Dettaglio con stringhe vuote / da pulire (verifica strip e skip)")
logger.reset_fase()
logger.info_mex(
    corpo="Test pulizia dettagli",
    dettaglio=["   Riga con spazi iniziali", "", "   ", "Riga normale", "Riga finale   "]
)


# ---------------------------------------------------------------
sezione("5. Fasi annidate a più livelli")
logger.reset_fase()
logger.new_phase("DROPBOX")
logger.info_mex("Connesso al Dropbox")

logger.new_phase("Smistamento file")
logger.info_mex("3 file trovati")

logger.new_phase("Controllo file: app_2026_07.xlsx")
logger.warning_mex("Colonna data non trovata -> SALTATO")
logger.end_phase()  # chiude "Controllo file"

logger.new_phase("Controllo file: app_2026_08.xlsx")
logger.info_mex("File conforme")
logger.end_phase()  # chiude "Controllo file"

logger.end_phase()  # chiude "Smistamento file"
logger.end_phase()  # chiude "DROPBOX"


# ---------------------------------------------------------------
sezione("6. reset_fase() nel mezzo del flusso - contatore deve ripartire da 1")
logger.reset_fase()
logger.new_phase("Prima fase mese 1")
logger.info_mex("Elaborazione mese 1")
logger.end_phase()

logger.reset_fase()
logger.new_phase("Prima fase mese 2 (deve essere di nuovo 'Fase 1')")
logger.info_mex("Elaborazione mese 2")
logger.end_phase()


# ---------------------------------------------------------------
sezione("7. Più fasi consecutive allo stesso livello (contatore deve incrementare)")
logger.reset_fase()
logger.new_phase("DROPBOX")
logger.info_mex("Fase 1 completata")
logger.end_phase()

logger.new_phase("PROCESSING")
logger.info_mex("Fase 2 completata")
logger.end_phase()

logger.new_phase("GOOGLE DRIVE")
logger.info_mex("Fase 3 completata")
logger.end_phase()


# ---------------------------------------------------------------
sezione("8. end_phase() chiamato più volte del dovuto (non deve andare sotto zero)")
logger.reset_fase()
logger.new_phase("Fase singola")
logger.end_phase()
logger.end_phase()  # extra, non dovrebbe rompere nulla
logger.end_phase()  # extra, non dovrebbe rompere nulla
logger.info_mex("Questo messaggio deve restare al livello 0 (nessuna indentazione)")


# ---------------------------------------------------------------
sezione("9. Simulazione realistica: flusso con errore a metà")
logger.reset_fase()
logger.new_phase("DROPBOX")
logger.info_mex("Connesso al Dropbox")

logger.new_phase("Verifica file")
logger.error_mex(
    corpo="Fallito il flusso per ANNO 2026 - MESE 07",
    dettaglio="Colonne mancanti nel foglio Spese: ['Data e ora', 'Categoria']"
)
logger.end_phase()
logger.end_phase()

logger.separatore()
logger.warning_mex(
    corpo="1 su 3 file hanno fallito:",
    dettaglio=["ANNO 2026 MESE 07: Colonne mancanti nel foglio Spese"]
)


# ---------------------------------------------------------------
sezione("10. Separatori e block")
logger.separatore()
print("Contenuto tra due separatori")
logger.separatore()


print("\n\nTEST COMPLETATO\n")