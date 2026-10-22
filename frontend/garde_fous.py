"""Garde-fous appliqués avant l'appel à l'agent (défense en profondeur)."""
import re

MESSAGE_REFUS = "Je ne peux vous communiquer que vos propres informations."

_MOTIF = re.compile(
    r"\b(?:assur[ée]e?s?|client|patient|ass)\s*[-:]?\s*"
    r"(?:n\s*°|no.?|numéro|numero)?\s*0*(\d+)",
    re.IGNORECASE,
)

def vise_autre_assure(question, assure_id):
    """Vrai si la question cite un numéro d'assuré différent de celui connecté."""
    for numero in _MOTIF.findall(question or ""):
        if int(numero) != assure_id:
            return True
    return False