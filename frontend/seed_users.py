"""Crée les comptes de démonstration et la table des paramètres."""
import secrets

from auth import connexion, hacher

MDP_DEMO = "Demo2026!"   # compte de DÉMO uniquement
COMPTES = [  # login, rôle, assure_id, nom affiché
    ("assure1", "assure", 1, "Assuré ASS-001 (CONFORT)"),
    ("assure2", "assure", 2, "Assuré ASS-002 (ESSENTIEL)"),
    ("assure3", "assure", 3, "Assuré ASS-003 (PREMIUM)"),
    ("pro1", "professionnel", None, "Professionnel de santé"),
    ("gest1", "gestionnaire", None, "Gestionnaire TPA"),
    ("admin1", "administrateur", None, "Administrateur"),
]

conn = connexion()
with conn.cursor() as cur:
    cur.execute("""
        DROP TABLE IF EXISTS utilisateurs_prov;
        CREATE TABLE utilisateurs_prov (
            id SERIAL PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            mdp_hash TEXT NOT NULL,
            sel TEXT NOT NULL,
            role TEXT NOT NULL,
            assure_id INT,
            nom_affiche TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS parametres (
            cle TEXT PRIMARY KEY,
            valeur TEXT NOT NULL
        );
        INSERT INTO parametres VALUES ('cache_seuil', '0.92')
        ON CONFLICT DO NOTHING;
    """)
    for login, role, assure_id, nom in COMPTES:
        sel = secrets.token_hex(16)
        cur.execute(
            """INSERT INTO utilisateurs_prov
               (login, mdp_hash, sel, role, assure_id, nom_affiche)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (login, hacher(MDP_DEMO, sel), sel, role, assure_id, nom))
conn.commit()
conn.close()
print("Comptes créés (mot de passe de démo :", MDP_DEMO, ")")
for c in COMPTES:
    print("  ", c[0], "->", c[1])