"""Initialisation automatique au premier démarrage (idempotente).

Lancé par le conteneur avant Streamlit : crée l'extension, charge les
documents, les données de démonstration, les comptes, le cache et le journal.
Chaque étape est ignorée si elle a déjà été faite : redémarrer ne perd rien.
"""
import os
import subprocess
import sys
import time

import psycopg2

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for dossier in ("rag", "agent", "frontend"):
    sys.path.insert(0, os.path.join(RACINE, dossier))


def log(message):
    print(f"[init] {message}", flush=True)


def connexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "test"))


def attendre_base(tentatives=60):
    for _ in range(tentatives):
        try:
            connexion().close()
            return True
        except psycopg2.OperationalError:
            time.sleep(2)
    return False


def existe(cur, table):
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table,))
    return cur.fetchone()[0]


def compter(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


def lancer(script):
    subprocess.run([sys.executable, os.path.join(RACINE, script)],
                   cwd=RACINE, check=True)


def etape(nom, fonction):
    try:
        fonction()
        log(f"{nom} : OK")
    except Exception as e:  # noqa: BLE001
        log(f"{nom} : ECHEC ({type(e).__name__}: {e})")


def parametres():
    conn = connexion()
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS parametres ("
                    "cle TEXT PRIMARY KEY, valeur TEXT NOT NULL)")
        cur.execute("INSERT INTO parametres VALUES ('cache_seuil', %s) "
                    "ON CONFLICT DO NOTHING",
                    (os.getenv("CACHE_SEUIL", "0.92"),))
    conn.commit()
    conn.close()


def tables_applicatives():
    import audit
    import cache
    cache.creer_table()
    audit.creer_table()


def main():
    log("attente de la base de données...")
    if not attendre_base():
        log("base inaccessible : arrêt de l'initialisation")
        return
    conn = connexion()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        docs_ok = (existe(cur, "documents_vectorises")
                   and compter(cur, "documents_vectorises") > 0)
        factures_ok = existe(cur, "factures_prov")
        users_ok = existe(cur, "utilisateurs_prov")
    conn.close()

    pdf_dir = os.path.join(RACINE, os.getenv("PDF_DIR", "data/pdf"))
    if docs_ok:
        log("documents déjà vectorisés : étape ignorée")
    elif os.path.isdir(pdf_dir) and any(
            f.lower().endswith(".pdf") for f in os.listdir(pdf_dir)):
        etape("Ingestion des documents", lambda: lancer("rag/ingestion.py"))
    else:
        log(f"PDF introuvables dans {pdf_dir} : placez-les puis relancez")

    if factures_ok:
        log("données de démonstration déjà présentes : étape ignorée")
    else:
        etape("Données de démonstration",
              lambda: lancer("agent/seed_provisoire.py"))

    if users_ok:
        log("comptes déjà créés : étape ignorée")
    else:
        etape("Comptes de démonstration",
              lambda: lancer("frontend/seed_users.py"))

    etape("Paramètres", parametres)
    etape("Tables du cache et du journal", tables_applicatives)
    log("initialisation terminée")


if __name__ == "__main__":
    main()
