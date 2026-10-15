"""Prouve que le code (et pas le LLM) isole les données de l'assuré connecté."""
from agent import executer_outil

ctx = {"assure_id": 1, "formule": "CONFORT"}

# Le LLM "triche" en passant assure_id=2 : le code doit l'ignorer.
res = executer_outil("mes_remboursements", {"assure_id": 2}, ctx)
assert "F-0007" not in res and "F-0008" not in res, "FUITE de données !"
assert "F-0005" in res, "Les factures de l'assuré 1 devraient apparaître"
print("OK : assure_id=2 ignoré, seules les factures de l'assuré 1 sortent.")

# Le compte lecture seule ne peut rien modifier.
from tools import connexion_ro
conn = connexion_ro()
try:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM factures_prov")
    print("ECHEC : le compte peut écrire !")
except Exception as e:
    print("OK : écriture refusée ->", type(e).__name__)
conn.close()