"""Ingestion des PDF dans PostgreSQL + pgvector.

Étapes : lire les PDF -> créer des chunks étiquetés -> calculer les
embeddings -> stocker dans la table `documents_vectorises`.
"""
import json
import os
import re
import sys

import pymupdf
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()

PDF_DIR = os.getenv("PDF_DIR", "data/pdf")
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
EMBED_DIM = 384  # taille des vecteurs de multilingual-e5-small

FORMULES = ["ESSENTIEL", "CONFORT", "PREMIUM"]
VILLES = ["Antananarivo", "Toamasina", "Antsirabe", "Mahajanga",
          "Toliara", "Fianarantsoa", "Antsiranana"]


# --------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------
def nettoyer(texte):
    """Remplace les retours à la ligne et espaces multiples par un espace."""
    if texte is None:
        return ""
    return re.sub(r"\s+", " ", str(texte)).strip()


def ligne_vide(row):
    return all(nettoyer(c) == "" for c in row)


# --------------------------------------------------------------------
# 1. Contrats : un chunk par article + un chunk par ligne de garantie
# --------------------------------------------------------------------
def chunks_contrat(chemin, formule):
    doc = pymupdf.open(chemin)
    chunks = []

    # --- a) découpage par article (texte) ---
    texte = "\n".join(page.get_text() for page in doc)
    # on retire les en-têtes répétés de chaque page
    texte = re.sub(r"DOCUMENT FICTIF[^\n]*\nPage \d+\n", "", texte)
    morceaux = re.split(r"(?m)^(?=Article \d+ – )", texte)
    for m in morceaux:
        m = m.strip()
        if not m.startswith("Article"):
            continue
        titre = m.split("\n")[0]
        num = re.match(r"Article (\d+)", titre).group(1)
        corps = nettoyer(m)
        chunks.append({
            "contenu": f"Contrat formule {formule} - {corps}",
            "type": "contrat",
            "formule": formule,
            "source": os.path.basename(chemin),
            "meta": {"article": int(num), "titre": nettoyer(titre)},
        })

    # --- b) tableau des garanties : une ligne = un chunk ---
    for page in doc:
        for tb in page.find_tables().tables:
            rows = tb.extract()
            if not rows or "Taux" not in nettoyer(rows[0][1] if len(rows[0]) > 1 else ""):
                continue
            for row in rows[1:]:
                if ligne_vide(row) or len(row) < 5:
                    continue
                cat, taux, plafond, franchise, carence = [nettoyer(c) for c in row[:5]]
                texte_g = (
                    f"Formule {formule}, catégorie {cat} : taux de remboursement "
                    f"{taux}, plafond annuel {plafond}, franchise par facture "
                    f"{franchise}, délai de carence {carence}."
                )
                chunks.append({
                    "contenu": texte_g, "type": "garantie", "formule": formule,
                    "source": os.path.basename(chemin),
                    "meta": {"categorie": cat, "taux": taux,
                             "plafond": plafond, "carence": carence},
                })
    return chunks


# --------------------------------------------------------------------
# 2. Barème : un chunk par acte, un chunk par médicament
# --------------------------------------------------------------------
def chunks_bareme(chemin):
    doc = pymupdf.open(chemin)
    chunks = []
    for page in doc:
        for tb in page.find_tables().tables:
            for row in tb.extract():
                row = [nettoyer(c) for c in row]
                if not row or row[0] in ("Code", "") or ligne_vide(row):
                    continue
                # Tableau des actes : 9 colonnes
                if len(row) >= 9 and row[3].endswith("Ar"):
                    code, lib, cat, mini, ref, maxi, ordo, ent, restr = row[:9]
                    texte = (f"Acte {code} ({lib}), catégorie {cat} : tarif minimum "
                             f"{mini}, tarif de référence {ref}, tarif maximum {maxi}. "
                             "La base de remboursement est plafonnée au tarif maximum.")
                    if ordo:
                        texte += " Ordonnance obligatoire."
                    if ent:
                        texte += " Entente préalable obligatoire."
                    if restr:
                        texte += f" Restriction : {restr}."
                    chunks.append({
                        "contenu": texte, "type": "bareme", "formule": None,
                        "source": os.path.basename(chemin),
                        "meta": {"code": code, "categorie": cat}})
                # Tableau des médicaments : 5 colonnes
                elif len(row) >= 5 and re.match(r"MED-", row[0]):
                    code, lib, classe, prix, remb = row[:5]
                    texte = (f"Médicament {code} ({lib}), classe {classe} : prix de "
                             f"référence {prix}. Remboursable : {remb}.")
                    chunks.append({
                        "contenu": texte, "type": "medicament", "formule": None,
                        "source": os.path.basename(chemin),
                        "meta": {"code": code, "classe": classe}})
    return chunks


# --------------------------------------------------------------------
# 3. Guide du réseau (National uniquement) : un chunk par prestataire
# --------------------------------------------------------------------
TITRES_SECTIONS = {
    "PHARMACIES": "Pharmacie",
    "GÉNÉRALISTES (CABINETS MÉDICAUX)": "Généraliste",
    "SPÉCIALISTES": "Spécialiste",
    "CLINIQUES ET CENTRES MÉDICAUX": "Clinique / Centre médical",
    "LABORATOIRES": "Laboratoire",
    "IMAGERIE MÉDICALE": "Imagerie médicale",
    "DENTISTES": "Dentiste",
    "OPTICIENS": "Opticien",
    "KINÉSITHÉRAPIE": "Kinésithérapeute",
    "MATERNITÉS": "Maternité",
}


def trouver_ville(adresse):
    for v in VILLES:
        if v.lower() in adresse.lower():
            return v
    return None


def titre_de_section(texte):
    """Retourne le titre de section si le bloc en est un, sinon None.

    Un bloc valide est soit le titre seul (ex. 'SPÉCIALISTES'), soit
    la ligne de description qui suit (ex. 'OPTICIENS = Ordonnance ...').
    La description est sur la même page que le tableau, même quand le
    titre est resté tout en bas de la page précédente.
    """
    for titre in TITRES_SECTIONS:
        motif = rf"{re.escape(titre)}(?: {re.escape(titre)})?(?: =|$)"
        if re.match(motif, texte):
            return titre
    return None


def chunks_guide(chemin):
    doc = pymupdf.open(chemin)
    chunks = []
    categorie = "Prestataire"
    for page in doc:
        blocs = page.get_text("blocks")
        for tb in page.find_tables().tables:
            y_tab = tb.bbox[1]
            candidats = []
            for b in blocs:
                if b[3] > y_tab + 2:      # bloc situé sous le tableau
                    continue
                titre = titre_de_section(nettoyer(b[4]))
                if titre:
                    candidats.append((b[3], titre))
            if candidats:
                categorie = TITRES_SECTIONS[max(candidats)[1]]
            for row in tb.extract():
                row = [nettoyer(c) for c in row]
                if len(row) < 6 or row[0] == "N°" or ligne_vide(row):
                    continue
                num, nom, horaires, contact, adresse, tarif = row[:6]
                ville = trouver_ville(adresse)
                texte = (f"Prestataire conventionné (catégorie : {categorie}, "
                         f"ville : {ville}) : {nom}. Horaires : {horaires}. "
                         f"Contact : {contact}. Adresse : {adresse}. "
                         f"Tarifs : {tarif}.")
                chunks.append({
                    "contenu": texte, "type": "prestataire", "formule": None,
                    "source": os.path.basename(chemin),
                    "meta": {"categorie": categorie, "ville": ville,
                             "nom": nom}})
    return chunks


# --------------------------------------------------------------------
# 4. Base de données
# --------------------------------------------------------------------
def connexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "test"),
    )


def creer_table(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS documents_vectorises (
                id SERIAL PRIMARY KEY,
                contenu TEXT NOT NULL,
                type TEXT NOT NULL,
                formule TEXT,
                source TEXT,
                meta JSONB,
                embedding vector({EMBED_DIM})
            );
            CREATE INDEX IF NOT EXISTS idx_docs_type ON documents_vectorises(type);
            CREATE INDEX IF NOT EXISTS idx_docs_formule ON documents_vectorises(formule);
        """)
    conn.commit()


def main():
    chunks = []
    for f in FORMULES:
        chunks += chunks_contrat(
            os.path.join(PDF_DIR, f"Conditions_Generales_{f}.pdf"), f)
    chunks += chunks_bareme(os.path.join(PDF_DIR, "Bareme_Reference_Actes.pdf"))
    chunks += chunks_guide(os.path.join(PDF_DIR, "Guide_Reseau_Soins_National.pdf"))

    # Résumé par type, pour vérifier à l'œil
    compte = {}
    for c in chunks:
        compte[c["type"]] = compte.get(c["type"], 0) + 1
    print("Chunks créés :", compte, "| total =", len(chunks))

    if "--dry-run" in sys.argv:
        par_cat, par_ville = {}, {}
        for c in chunks:
            if c["type"] == "prestataire":
                k = c["meta"]["categorie"]
                par_cat[k] = par_cat.get(k, 0) + 1
                v = c["meta"]["ville"]
                par_ville[v] = par_ville.get(v, 0) + 1
        print("\nPrestataires par catégorie :", par_cat)
        print("Prestataires par ville :", par_ville)

        for t in compte:
            ex = next(c for c in chunks if c["type"] == t)
            print(f"\n[{t}] exemple :\n{ex['contenu']}")
        print("\nMode test : rien n'est écrit en base.")
        return

    print("Chargement du modèle d'embeddings (1er lancement : téléchargement)...")
    model = SentenceTransformer(MODEL_NAME)
    # Le modèle e5 exige le préfixe "passage: " pour les documents
    textes = ["passage: " + c["contenu"] for c in chunks]
    vecteurs = model.encode(textes, batch_size=32, show_progress_bar=True,
                            normalize_embeddings=True)

    conn = connexion()
    creer_table(conn)
    with conn.cursor() as cur:
        cur.execute("TRUNCATE documents_vectorises RESTART IDENTITY;")
        for c, v in zip(chunks, vecteurs):
            cur.execute(
                """INSERT INTO documents_vectorises
                   (contenu, type, formule, source, meta, embedding)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (c["contenu"], c["type"], c["formule"], c["source"],
                 json.dumps(c["meta"], ensure_ascii=False), v),
            )
    conn.commit()
    conn.close()
    print(f"{len(chunks)} chunks stockés dans documents_vectorises.")


if __name__ == "__main__":
    main()