"""Authentification branchée sur la table users du backend + Token JWT."""
import os
import psycopg2
import bcrypt
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://backend:8000")

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
    """Vérifie en base locale + récupère le Token JWT de l'API pour /predict"""
    _, lignes = requete("SELECT username, hashed_password, role FROM users WHERE username = %s", (login,))
    if not lignes:
        return None
    
    username, hashed_password, role = lignes[0]
    
    try:
        if not bcrypt.checkpw(mot_de_passe.encode('utf-8'), hashed_password.encode('utf-8')):
            return None
    except Exception:
        return None

    # Récupérer le token pour tester la fraude via l'interface
    token = ""
    try:
        r = requests.post(f"{API_URL}/auth/login", data={"username": login, "password": mot_de_passe}, timeout=5)
        if r.status_code == 200:
            token = r.json().get("access_token", "")
    except Exception:
        pass

    return {
        "login": username, 
        "role": "administrateur" if role == "admin" else role, # Uniformisation du rôle
        "assure_id": 1, 
        "nom": username.capitalize(), 
        "formule": "CONFORT",
        "token": token
    }