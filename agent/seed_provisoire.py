"""Tables PROVISOIRES pour développer l'agent (à remplacer par le vrai schéma)."""
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SQL = """
DROP TABLE IF EXISTS factures_prov;
DROP TABLE IF EXISTS assures_prov;

CREATE TABLE assures_prov (
    id SERIAL PRIMARY KEY,
    pseudo TEXT NOT NULL,
    formule TEXT NOT NULL,
    date_adhesion DATE NOT NULL
);

CREATE TABLE factures_prov (
    id SERIAL PRIMARY KEY,
    numero TEXT NOT NULL,
    assure_id INT NOT NULL REFERENCES assures_prov(id),
    date_soins DATE NOT NULL,
    categorie TEXT NOT NULL,
    prestataire TEXT NOT NULL,
    montant_facture INT NOT NULL,
    montant_rembourse INT NOT NULL,
    statut TEXT NOT NULL,          -- EN_COURS, PAYEE, REJETEE
    motif_rejet TEXT
);

INSERT INTO assures_prov (pseudo, formule, date_adhesion) VALUES
 ('ASS-001', 'CONFORT',   '2025-01-01'),
 ('ASS-002', 'ESSENTIEL', '2026-03-01'),
 ('ASS-003', 'PREMIUM',   '2025-06-01');

INSERT INTO factures_prov
 (numero, assure_id, date_soins, categorie, prestataire,
  montant_facture, montant_rembourse, statut, motif_rejet) VALUES
 ('F-0001', 1, '2026-02-10', 'Consultation', 'Docteur RAARISOA Vola', 20000, 18000, 'PAYEE', NULL),
 ('F-0002', 1, '2026-03-15', 'Pharmacie', 'Pharmacie Fanantenana', 35000, 31500, 'PAYEE', NULL),
 ('F-0003', 1, '2026-05-02', 'Laboratoire', 'Bio-Labo Lalaina', 42000, 37800, 'PAYEE', NULL),
 ('F-0004', 1, '2026-07-20', 'Dentaire', 'Cabinet Dentaire Dr RABEKOTONIRINA', 80000, 64000, 'PAYEE', NULL),
 ('F-0005', 1, '2026-09-05', 'Imagerie', 'Centre d''Imagerie Hoavy', 180000, 0, 'REJETEE', 'ENTENTE_PREALABLE_ABSENTE'),
 ('F-0006', 1, '2026-10-08', 'Consultation', 'Docteur RANAIVO Vola', 25500, 0, 'EN_COURS', NULL),
 ('F-0007', 2, '2026-04-12', 'Consultation', 'Docteur RAKOTOSOA Hasina', 17000, 13600, 'PAYEE', NULL),
 ('F-0008', 2, '2026-05-01', 'Optique', 'Optique Zina', 90000, 0, 'REJETEE', 'DELAI_DE_CARENCE'),
 ('F-0009', 3, '2026-06-18', 'Hospitalisation', 'Polyclinique Tanjaka', 900000, 900000, 'PAYEE', NULL);

DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent_ro') THEN
    CREATE ROLE agent_ro LOGIN PASSWORD 'agent_ro';
  END IF;
END $$;
GRANT CONNECT ON DATABASE predicare TO agent_ro;
GRANT USAGE ON SCHEMA public TO agent_ro;
GRANT SELECT ON assures_prov, factures_prov TO agent_ro;
"""

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "predicare"), user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "test"))
with conn.cursor() as cur:
    cur.execute(SQL)
conn.commit()
conn.close()
print("Tables provisoires et compte agent_ro créés.")