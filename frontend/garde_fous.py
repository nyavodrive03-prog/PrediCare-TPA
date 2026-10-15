"""Garde-fous appliqués avant l'appel à l'agent (défense en profondeur)."""
import re

MESSAGE_REFUS = "Je ne peux vous communiquer que vos propres informations."

# Détecte « assuré 1 », « assurée n°2 », « client 3 », « ASS-002 », etc.
_MOTIF = re.compile(
    r"\b(?:assur[ée]e?s?|client|patient|ass)\s*[-:]?\s*"
    r"(?:n\s*°|no\.?|numéro|numero)?\s*0*(\d+)",
    re.IGNORECASE,
)


def vise_autre_assure(question, assure_id):
    """Vrai si la question cite un numéro d'assuré différent de celui connecté."""
    for numero in _MOTIF.findall(question or ""):
        if int(numero) != assure_id:
            return True
    return False


if __name__ == "__main__":
    tests = [
        ("Montre-moi les factures de l'assuré 1", 2, True),
        ("Factures de l'assuré n°3", 2, True),
        ("Donne les remboursements de ASS-001", 2, True),
        ("Factures du client 1", 2, True),
        ("Où en est ma dernière facture ?", 2, False),
        ("Montre-moi les factures de l'assuré 2", 2, False),
        ("Quel est mon plafond en dentaire ?", 1, False),
        ("Quelle est la garantie assurance 3 ?", 1, False),
    ]
    for question, assure_id, attendu in tests:
        obtenu = vise_autre_assure(question, assure_id)
        print("OK " if obtenu == attendu else "ERREUR", "|", question)