"""Authentification (API de l'équipe ou provisoire) + accès base pour le frontend."""
import hashlib
import os
import secrets

import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://backend:8000")
AUTH_MODE = os.getenv("AUTH_MODE", "api")   # "api" (équipe) ou "local" (provisoire)

# Rôles de l'API -> rôles de ce frontend
ROLE_MAP = {
    "admin": "administrateur",
    "gestionnaire": "gestionnaire",
    "professionnel": "professionnel",
    "assure": "assure",
}


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


def verifier_local(login, mot_de_passe):
    """Login provisoire (table utilisateurs_prov). Retourne un dict ou None."""
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


def verifier_api(login, mot_de_passe):
    """Authentifie via POST /auth/login de l'équipe. Retourne le dict utilisateur ou None."""
    try:
        r = requests.post(f"{API_URL}/auth/login",
                          data={"username": login, "password": mot_de_passe},
                          timeout=10)
    except requests.RequestException as e:
        print(f"[auth] API injoignable : {e}")
        return None
    if r.status_code != 200:
        return None
    body = r.json()
    role = ROLE_MAP.get(body.get("role"))
    if role is None:          # rôle inconnu : on refuse
        return None
    # Profil provisoire (assuré lié, formule), en attendant la liaison dans leur schéma
    _, lignes = requete(
        """SELECT u.assure_id, u.nom_affiche, a.formule
           FROM utilisateurs_prov u
           LEFT JOIN assures_prov a ON a.id = u.assure_id
           WHERE u.login = %s""", (login,))
    assure_id, nom, formule = lignes[0] if lignes else (None, login, None)
    return {"login": login, "role": role, "assure_id": assure_id,
            "nom": nom or login, "formule": formule,
            "token": body["access_token"]}


def verifier(login, mot_de_passe):
    """Point d'entrée utilisé par app.py."""
    if AUTH_MODE == "local":
        return verifier_local(login, mot_de_passe)
    return verifier_api(login, mot_de_passe)