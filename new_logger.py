_contatore_phase = 0
_profonditá = 0

def new_phase(corpo: str):
if _contatoee_phase == 0:
print(f"Fase {_contatore_phase} - {corpo})
else:
print(f"- {corpo}")
_profonditá = _profonditá + 1


def end_phase:
_pronfonditá = max(0, _profonditá -1)

def get_tab(n: int)
return "\t" * n


def tipe(tipo: str, corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo = tipo.strip()
    corpo = corpo.strip()
    print(f"{get_tab(_profonditá)}[{tipo}]\t- {corpo}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:  # salta eventuali stringhe vuote nella lista
            print(f"{get_tab(_profonditá)}\t{mex}")