"""Cache sémantique : réponses aux questions documentaires déjà posées."""
import json
import os
import sys

import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rag"))
from retrieval import get_model  # noqa: E402

load_dotenv()


def _conn():
    """Connexion PostgreSQL avec le type vector enregistré."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "test"))
    register_vector(conn)
    return conn


def _ttl():
    """Durée de validité d'une entrée du cache, en heures."""
    return int(os.getenv("CACHE_TTL_HEURES", "24"))


def _seuil():
    """Seuil lu en base (modifiable depuis l'écran admin), sinon .env."""
    try:
        conn = _conn()
        with conn.cursor() as cur:
            cur.execute("SELECT valeur FROM parametres WHERE cle = 'cache_seuil'")
            ligne = cur.fetchone()
        conn.close()
        if ligne:
            return float(ligne[0])
    except Exception:  # noqa: BLE001
        pass
    return float(os.getenv("CACHE_SEUIL", "0.92"))


def creer_table():
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cache_semantique (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                formule TEXT NOT NULL,
                reponse TEXT NOT NULL,
                outils JSONB,
                embedding vector(384),
                cree_le TIMESTAMPTZ DEFAULT now(),
                nb_hits INT DEFAULT 0
            );""")
    conn.commit()
    conn.close()


def _vecteur(question):
    return get_model().encode("query: " + question, normalize_embeddings=True)


def chercher(question, formule):
    """Retourne (reponse, similarite) si une question proche existe, sinon None."""
    v = _vecteur(question)
    seuil = _seuil()
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, reponse, 1 - (embedding <=> %s) AS sim
               FROM cache_semantique
               WHERE formule = %s
                 AND cree_le > now() - (%s || ' hours')::interval
               ORDER BY embedding <=> %s LIMIT 1""",
            (v, formule, str(_ttl()), v))
        ligne = cur.fetchone()
        if ligne and ligne[2] >= seuil:
            cur.execute("UPDATE cache_semantique SET nb_hits = nb_hits + 1 "
                        "WHERE id = %s", (ligne[0],))
            conn.commit()
            conn.close()
            return ligne[1], float(ligne[2])
    conn.close()
    return None


def enregistrer(question, formule, reponse, outils):
    v = _vecteur(question)
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO cache_semantique
               (question, formule, reponse, outils, embedding)
               VALUES (%s, %s, %s, %s, %s)""",
            (question, formule, reponse,
             json.dumps(outils, ensure_ascii=False), v))
    conn.commit()
    conn.close()


def vider():
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE cache_semantique RESTART IDENTITY")
    conn.commit()
    conn.close()