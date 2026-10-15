"""Recherche sémantique dans pgvector, filtrée par formule d'assuré."""
import os

import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
_model = None  # chargé une seule fois, puis réutilisé


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def connexion():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "test"),
    )
    register_vector(conn)
    return conn


def rechercher(question, formule=None, types=None, k=5):
    """Retourne les k passages les plus proches de la question.

    formule : 'ESSENTIEL', 'CONFORT' ou 'PREMIUM'. Si fourni, les chunks
              d'AUTRES formules sont exclus (ceux sans formule restent).
    types   : liste optionnelle, ex. ['prestataire'] pour restreindre.
    """
    vecteur = get_model().encode("query: " + question,
                                 normalize_embeddings=True)
    conditions, params = [], [vecteur]
    if formule:
        conditions.append("(formule = %s OR formule IS NULL)")
        params.append(formule)
    if types:
        conditions.append("type = ANY(%s)")
        params.append(types)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params += [vecteur, k]

    sql = f"""
        SELECT contenu, type, formule, source, meta,
               embedding <=> %s AS distance
        FROM documents_vectorises
        {where}
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    conn = connexion()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        lignes = cur.fetchall()
    conn.close()
    return [
        {"contenu": l[0], "type": l[1], "formule": l[2],
         "source": l[3], "meta": l[4], "distance": float(l[5])}
        for l in lignes
    ]


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Quel est le délai de carence en optique ?"
    for r in rechercher(q, formule="CONFORT"):
        print(f"[{r['distance']:.3f}] ({r['type']}) {r['contenu'][:160]}\n")