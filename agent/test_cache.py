"""Mesure le gain du cache sémantique."""
import time

import cache
from agent import agent

cache.creer_table()
cache.vider()
ctx = {"assure_id": 1, "formule": "CONFORT"}

QUESTIONS = [
    ("Quel est mon plafond en dentaire ?", "1re fois (LLM)"),
    ("Quel est mon plafond en dentaire ?", "identique (cache)"),
    ("Quel plafond ai-je pour le dentaire ?", "reformulée (cache)"),
    ("Où en est ma dernière facture ?", "compte perso (jamais en cache)"),
    ("Où en est ma dernière facture ?", "compte perso, 2e fois (LLM)"),
]
for q, etiquette in QUESTIONS:
    t = time.time()
    r = agent(q, ctx)
    print(f"{time.time() - t:5.1f} s | cache={r['cache']!s:5} | "
          f"{etiquette} | {q}")