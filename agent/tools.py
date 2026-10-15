"""Outils de l'agent. L'identité de l'assuré vient de ctx, jamais du LLM."""
import os
import sys

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rag"))
from retrieval import rechercher  # noqa: E402

load_dotenv()


def connexion_ro():
    """Compte LECTURE SEULE : même une injection ne peut rien modifier."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "predicare"),
        user=os.getenv("DB_RO_USER", "agent_ro"),
        password=os.getenv("DB_RO_PASSWORD", "agent_ro"))


def chercher_documents(ctx, question="", **_):
    """Règles, garanties, barème, prestataires (RAG), filtré sur la formule."""
    passages = rechercher(question, formule=ctx["formule"], k=5)
    return "\n".join(f"[{i}] {p['contenu']}" for i, p in enumerate(passages, 1))


def mes_remboursements(ctx, statut=None, **_):
    """Les 10 dernières factures de l'assuré connecté."""
    sql = """SELECT numero, date_soins, categorie, prestataire, montant_facture,
                    montant_rembourse, statut, motif_rejet
             FROM factures_prov WHERE assure_id = %s"""
    params = [ctx["assure_id"]]
    if statut in ("EN_COURS", "PAYEE", "REJETEE"):
        sql += " AND statut = %s"
        params.append(statut)
    sql += " ORDER BY date_soins DESC LIMIT 10"
    conn = connexion_ro()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        lignes = cur.fetchall()
    conn.close()
    if not lignes:
        return "Aucune facture trouvée pour cet assuré."
    return "\n".join(
        f"Facture {n} du {d} : {c} chez {p}, facturé {mf} Ar, remboursé {mr} Ar, "
        f"statut {s}" + (f", motif de rejet {m}" if m else "")
        for n, d, c, p, mf, mr, s, m in lignes)


def ma_consommation(ctx, annee=2026, **_):
    """Montants remboursés par catégorie pour l'année (factures PAYEE).

    Le TOTAL est calculé ici, par le code : le LLM ne doit jamais additionner.
    """
    conn = connexion_ro()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT categorie, SUM(montant_rembourse) FROM factures_prov
               WHERE assure_id = %s AND statut = 'PAYEE'
                 AND EXTRACT(YEAR FROM date_soins) = %s
               GROUP BY categorie ORDER BY categorie""",
            (ctx["assure_id"], int(annee)))
        lignes = cur.fetchall()
    conn.close()
    if not lignes:
        return f"Aucune consommation remboursée en {annee}."
    total = sum(int(t) for _, t in lignes)
    detail = "; ".join(f"{c} : {int(t)} Ar" for c, t in lignes)
    return (f"Consommation {annee} (remboursée) : {detail}. "
            f"TOTAL {annee} : {total} Ar (déjà calculé, à recopier tel quel).")


# Outils disponibles (nom -> fonction)
TOOLS = {"chercher_documents": chercher_documents,
         "mes_remboursements": mes_remboursements,
         "ma_consommation": ma_consommation}

# Description donnée au LLM (aucun paramètre d'identité !)
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "chercher_documents",
        "description": "Cherche dans les contrats, garanties, barème des actes, "
                       "médicaments et annuaire des prestataires.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string",
                         "description": "La question à rechercher"}},
            "required": ["question"]}}},
    {"type": "function", "function": {
        "name": "mes_remboursements",
        "description": "Liste les factures de l'assuré connecté avec leur statut "
                       "(EN_COURS, PAYEE, REJETEE) et le motif de rejet. À utiliser "
                       "pour toute question sur un dossier, une facture, un rejet "
                       "ou un remboursement en attente. Sans paramètre statut, "
                       "elle renvoie toutes les factures.",
        "parameters": {"type": "object", "properties": {
            "statut": {"type": "string",
                       "enum": ["EN_COURS", "PAYEE", "REJETEE"]}}}}},
    {"type": "function", "function": {
        "name": "ma_consommation",
        "description": "Total remboursé par catégorie de soins pour une année.",
        "parameters": {"type": "object", "properties": {
            "annee": {"type": "integer"}}}}},
]