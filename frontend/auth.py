"""Authentification et accès base pour le frontend."""
import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def connexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare_db"),
        user=os.getenv("DB_USER", "predicare"),
        password=os.getenv("DB_PASSWORD", "predicare123"))

def requete(sql, params=None):
    """Exécute un SELECT et retourne (colonnes, lignes)."""
    conn = connexion()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        colonnes = [d[0] for d in cur.description]
        lignes = cur.fetchall()
    conn.close()
    return colonnes, lignes

def verifier(login, mot_de_passe):
    """Retourne un dict utilisateur si le login est bon, sinon None."""
    _, lignes = requete(
        "SELECT username, hashed_password, role FROM users WHERE username = %s", 
        (login,)
    )
    
    if not lignes:
        return None
    
    username, hashed_password, role = lignes[0]
    
    try:
        if not bcrypt.checkpw(mot_de_passe.encode('utf-8'), hashed_password.encode('utf-8')):
            return None
    except Exception as e:
        print(f"Erreur de vérification bcrypt : {e}")
        return None

    return {
        "login": username, 
        "role": role, 
        "assure_id": 1, 
        "nom": username.capitalize(), 
        "formule": "CONFORT"
    }