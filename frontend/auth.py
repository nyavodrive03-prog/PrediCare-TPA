"""Authentification branchée sur la table users du backend."""
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

def verifier(login, mot_de_passe):
    """Retourne un dict utilisateur si le login est bon, sinon None."""
    conn = connexion()
    with conn.cursor() as cur:
        # On interroge la table users du backend
        cur.execute("SELECT username, hashed_password, role FROM users WHERE username = %s", (login,))
        ligne = cur.fetchone()
    conn.close()

    if not ligne:
        return None
    
    username, hashed_password, role = ligne
    
    # Vérification directe avec bcrypt (sans passlib)
    try:
        # bcrypt.checkpw a besoin d'octets (bytes) en entrée
        if not bcrypt.checkpw(mot_de_passe.encode('utf-8'), hashed_password.encode('utf-8')):
            return None
    except Exception as e:
        print(f"Erreur de vérification bcrypt : {e}")
        return None

    # On adapte le retour pour que le reste de ton app.py continue de fonctionner
    return {
        "login": username, 
        "role": role, 
        "assure_id": 1, 
        "nom": username.capitalize(), 
        "formule": "CONFORT"
    }