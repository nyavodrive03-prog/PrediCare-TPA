"""Authentification provisoire + accès base pour le frontend."""
import hashlib
import os
import secrets

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "test"))


def requete(sql, params=None):
    """Exécute un SELECT et retourne (colonnes, lignes)."""
    conn = connexion()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        colonnes = [d[0] for d in cur.description]
        lignes = cur.fetchall()
    conn.close()
    return colonnes, lignes


def hacher(mot_de_passe, sel_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), bytes.fromhex(sel_hex), 200_000).hex()


def verifier(login, mot_de_passe):
    """Retourne un dict utilisateur si le login est bon, sinon None."""
    _, lignes = requete(
        """SELECT u.login, u.mdp_hash, u.sel, u.role, u.assure_id,
                  u.nom_affiche, a.formule
           FROM utilisateurs_prov u
           LEFT JOIN assures_prov a ON a.id = u.assure_id
           WHERE u.login = %s""", (login,))
    if not lignes:
        hacher(mot_de_passe, "00" * 16)  # même durée : pas de fuite d'info
        return None
    lg, mdp_hash, sel, role, assure_id, nom, formule = lignes[0]
    if not secrets.compare_digest(hacher(mot_de_passe, sel), mdp_hash):
        return None
    return {"login": lg, "role": role, "assure_id": assure_id,
            "nom": nom, "formule": formule}