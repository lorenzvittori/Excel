_contatore_fase = 0
_profondita = 0


def get_tab(n: int) -> str:
    return "\t" * 2*n


def new_phase(corpo: str) -> None:
    global _contatore_fase, _profondita
    corpo = corpo.strip()

    if _profondita == 0:
        _contatore_fase += 1
        print(f"Fase {_contatore_fase}: {corpo}")
    else:
        print(f"{get_tab(_profondita)}• {corpo}")

    _profondita += 1


def end_phase() -> None:
    global _profondita
    _profondita = max(0, _profondita - 1)


def tipo_messaggio(tipo: str, corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo = tipo.strip()
    corpo = corpo.strip()
    print(f"{get_tab(_profondita)}[{tipo}]: \t{corpo}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:
            print(f"{get_tab(_profondita)}\t{mex}")


def reset_fase(valore_iniziale: int = 0) -> None:
    global _contatore_fase, _profondita
    _contatore_fase = valore_iniziale
    _profondita = 0