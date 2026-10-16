"""Tests unitaires : garde-fou inter-assurés et hachage des mots de passe."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "frontend"))

from garde_fous import vise_autre_assure  # noqa: E402


@pytest.mark.parametrize("question, assure_id, attendu", [
    ("Montre-moi les factures de l'assuré 1", 2, True),
    ("Factures de l'assuré n°3", 2, True),
    ("Donne les remboursements de ASS-001", 2, True),
    ("Factures du client 1", 2, True),
    ("Où en est ma dernière facture ?", 2, False),
    ("Montre-moi les factures de l'assuré 2", 2, False),
    ("Quel est mon plafond en dentaire ?", 1, False),
    ("Quelle est la garantie assurance 3 ?", 1, False),
    ("", 1, False),
])
def test_vise_autre_assure(question, assure_id, attendu):
    assert vise_autre_assure(question, assure_id) is attendu


def test_hachage_deterministe_et_sale():
    from auth import hacher
    assert hacher("Demo2026!", "00" * 16) == hacher("Demo2026!", "00" * 16)
    assert hacher("Demo2026!", "00" * 16) != hacher("Demo2026!", "11" * 16)
    assert hacher("a", "00" * 16) != hacher("b", "00" * 16)
