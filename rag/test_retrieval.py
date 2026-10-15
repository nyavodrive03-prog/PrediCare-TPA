"""Teste si la recherche ramène le bon passage dans les 3 premiers."""
from retrieval import rechercher

# (question, formule, mot-clé attendu dans un des 3 premiers résultats)
TESTS = [
    ("Quel est le délai de carence en optique ?", "CONFORT", "90 jours"),
    ("Quel est le taux de remboursement du dentaire ?", "ESSENTIEL", "70 %"),
    ("Quel est le plafond annuel global ?", "PREMIUM", "20 000 000"),
    ("Quels documents faut-il pour un scanner ?", "CONFORT", "entente"),
    ("Quels sont les motifs de rejet d'un dossier ?", "ESSENTIEL",
     "DELAI_DE_CARENCE"),
    ("Quelle pharmacie est ouverte 24h/24 à Toamasina ?", "CONFORT",
     "Toamasina"),
    ("Quel est le tarif maximum d'une IRM ?", "PREMIUM", "1 600 000"),
    ("La prothèse dentaire est-elle couverte par ESSENTIEL ?", "ESSENTIEL",
     "DENT-PROTH"),
]

ok = 0
for question, formule, attendu in TESTS:
    res = rechercher(question, formule=formule, k=3)
    trouve = any(attendu.lower() in r["contenu"].lower() for r in res)
    ok += trouve
    print(("OK  " if trouve else "ECHEC"), "|", question, f"(cherché : {attendu})")
    if not trouve:
        for r in res:
            print("      ->", r["contenu"][:110])
print(f"\nScore : {ok}/{len(TESTS)}")