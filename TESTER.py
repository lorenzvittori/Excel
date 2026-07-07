## NOME FILE: test_new_logger.py
"""
Script dimostrativo per esplorare l'utilizzo di new_logger.py
Simula un flusso realistico simile a FLUSSO_TOTALE.py, con fasi annidate,
messaggi di vario tipo, e reset tra "run" successive.
"""

import new_logger as logger


def simula_run(anno: str, mese: str, forza_errore: bool = False) -> None:
    logger.reset_fase()

    logger.new_phase("DROPBOX")
    logger.tipo_messaggio("INFO", f"Connessione al Dropbox per {anno}-{mese}")

    logger.new_phase("Verifica file raw")
    logger.tipo_messaggio("INFO", "File trovato: app_2026_07.xlsx")

    if forza_errore:
        logger.tipo_messaggio(
            "ERROR",
            "Colonne mancanti nel foglio Spese",
            dettaglio=["Data e ora", "Categoria", "Importo in valuta del conto"]
        )
        logger.end_phase()
        logger.end_phase()
        return

    logger.tipo_messaggio("OK", "Struttura del file conforme")
    logger.end_phase()  # chiude "Verifica file raw"
    logger.end_phase()  # chiude "DROPBOX"

    logger.new_phase("PROCESSING")
    logger.tipo_messaggio("INFO", "Pulizia e formattazione in corso")
    logger.tipo_messaggio(
        "WARNING",
        "Trovati record duplicati",
        dettaglio=["Riga 12: Cibo Fuori 20,00", "Riga 45: Cibo Fuori 20,00"]
    )
    logger.end_phase()  # chiude "PROCESSING"

    logger.new_phase("GOOGLE DRIVE")

    logger.new_phase("Connessione al client")
    logger.tipo_messaggio("OK", "Client autorizzato correttamente")
    logger.end_phase()

    logger.new_phase("Scrittura sul foglio")
    logger.tipo_messaggio("INFO", "Celle B2:D550 svuotate prima della scrittura")
    logger.tipo_messaggio("OK", "Scrittura completata")
    logger.end_phase()

    logger.end_phase()  # chiude "GOOGLE DRIVE"


if __name__ == "__main__":
    print("="*60)
    print("DEMO 1 - Run singola, tutto ok")
    print("="*60)
    simula_run(anno="2026", mese="07")

    print()
    print("="*60)
    print("DEMO 2 - Run con errore (colonne mancanti)")
    print("="*60)
    simula_run(anno="2026", mese="08", forza_errore=True)

    print()
    print("="*60)
    print("DEMO 3 - Loop su più mesi, con reset_fase() a ogni iterazione")
    print("="*60)
    for mese_corrente in ["06", "07"]:
        print(f"\n--- Elaborazione mese {mese_corrente} ---")
        simula_run(anno="2026", mese=mese_corrente)

    print()
    print("="*60)
    print("DEMO 4 - Messaggi senza dettaglio, con dettaglio stringa singola, con lista")
    print("="*60)
    logger.reset_fase()
    logger.tipo_messaggio("INFO", "Messaggio semplice, senza dettagli")
    logger.tipo_messaggio("WARNING", "Messaggio con un solo dettaglio", dettaglio="Controlla il file X")
    logger.tipo_messaggio(
        "ERROR",
        "Messaggio con più dettagli",
        dettaglio=["Primo dettaglio", "Secondo dettaglio", "  Terzo con spazi da pulire  "]
    )