"""Interface web PrediCare TPA : login + parcours par rôle."""
import os
import sys
import time

import requests
import streamlit as st

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "rag"))
sys.path.insert(0, os.path.join(RACINE, "agent"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(RACINE, ".env"))

import audit  # noqa: E402
import auth  # noqa: E402
import cache  # noqa: E402
import garde_fous  # noqa: E402
from agent import agent as poser_question  # noqa: E402
from generation import repondre as repondre_documents  # noqa: E402
from retrieval import rechercher  # noqa: E402

st.set_page_config(page_title="PrediCare TPA", page_icon="🏥", layout="wide")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ROLES = {"assure": "Assuré", "professionnel": "Professionnel de santé",
         "gestionnaire": "Gestionnaire", "administrateur": "Administrateur"}


# --------------------------------------------------------------------
# Outils d'affichage
# --------------------------------------------------------------------
def tableau(sql, params=None):
    colonnes, lignes = auth.requete(sql, params)
    st.dataframe([dict(zip(colonnes, l)) for l in lignes],
                 use_container_width=True, hide_index=True)
    return lignes


def afficher_sources(sources, titre):
    with st.expander(titre):
        for i, s in enumerate(sources, 1):
            st.write(f"**[{i}]** ({s['type']}) {s['contenu']}")


def afficher_chat(fonction, cle, user, titre_sources="Passages utilisés"):
    """fonction(question) -> (texte, info, origine, sources).

    origine : cache | llm | refus | documents (alimente le journal d'audit).
    Garde l'historique en session et journalise chaque question.
    """
    historique = st.session_state.setdefault(cle, [])
    for m in historique:
        with st.chat_message(m["role"]):
            st.markdown(m["texte"])
            if m.get("info"):
                st.caption(m["info"])
            if m.get("sources"):
                afficher_sources(m["sources"], titre_sources)
    question = st.chat_input("Posez votre question...")
    if not question:
        return
    historique.append({"role": "user", "texte": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Je cherche la réponse..."):
            debut = time.perf_counter()
            sources, statut = None, "ok"
            try:
                texte, info, origine, sources = fonction(question)
            except Exception as e:  # noqa: BLE001
                texte = ("Le service est momentanément indisponible. "
                         "Contactez PrediCare au 034 00 000 02.")
                info, origine, statut = (
                    f"Erreur technique : {type(e).__name__}", "erreur",
                    "erreur")
            duree = time.perf_counter() - debut
            info = f"{info} · {duree:.1f} s"
        audit.journaliser(user["login"], user["role"], "question", origine,
                          int(duree * 1000), statut)
        st.markdown(texte)
        st.caption(info)
        if sources:
            afficher_sources(sources, titre_sources)
    historique.append({"role": "assistant", "texte": texte, "info": info,
                       "sources": sources})


# --------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------
def page_assistant(user):
    st.header("Assistant virtuel")
    st.caption("Posez vos questions sur votre contrat ou vos remboursements.")

    def fn(q):
        # Garde-fou : refus avant tout appel à l'agent ou au LLM
        if garde_fous.vise_autre_assure(q, user["assure_id"]):
            return (garde_fous.MESSAGE_REFUS,
                    "🛡️ Demande refusée (aucune donnée lue)", "refus", None)
        res = poser_question(q, {"assure_id": user["assure_id"],
                                 "formule": user["formule"]})
        noms = {n for n, _ in res.get("outils", [])}
        if res.get("cache"):
            origine = "cache"
            info = f"⚡ Réponse du cache (similarité {res['similarite']})"
        else:
            origine = "llm"
            info = (f"🤖 Générée par le LLM · outils : "
                    f"{', '.join(sorted(noms)) or 'aucun'}")
        # Réponse sourcée : passages du contrat les plus proches de la question
        sources = None
        if res.get("cache") or "chercher_documents" in noms:
            try:
                trouves = rechercher(q, formule=user["formule"], k=5)
                utiles = [p for p in trouves if p["type"] != "prestataire"]
                sources = (utiles or trouves)[:3]
            except Exception:  # noqa: BLE001
                sources = None
        return res["reponse"], info, origine, sources

    afficher_chat(fn, "chat_assure", user,
                  "Passages de référence (documents du contrat)")


def page_mes_factures(user):
    st.header("Mes factures")
    st.caption(f"Formule : {user['formule']}")
    tableau("""SELECT numero AS "N°", date_soins AS "Date", categorie AS "Catégorie",
                      prestataire AS "Prestataire", montant_facture AS "Facturé (Ar)",
                      montant_rembourse AS "Remboursé (Ar)", statut AS "Statut",
                      motif_rejet AS "Motif de rejet"
               FROM factures_prov WHERE assure_id = %s
               ORDER BY date_soins DESC""", (user["assure_id"],))


def page_pro(user):
    st.header("Contrats, barème et réseau")
    st.caption("Consultez les règles de prise en charge. "
               "Choisissez la formule du patient.")
    formule = st.selectbox("Formule du patient",
                           ["ESSENTIEL", "CONFORT", "PREMIUM"])

    def fn(q):
        res = repondre_documents(q, formule=formule)
        return (res["reponse"], f"📄 Documents (formule {formule})",
                "documents", res["sources"])

    afficher_chat(fn, "chat_pro", user,
                  "Passages utilisés pour cette réponse")


def page_gestionnaire(user):
    st.header("Tableau de bord gestionnaire")
    _, lignes = auth.requete(
        """SELECT COUNT(*), COALESCE(SUM(montant_facture),0),
                  COALESCE(SUM(montant_rembourse),0),
                  COUNT(*) FILTER (WHERE statut = 'REJETEE')
           FROM factures_prov""")
    n, facture, rembourse, rejetees = lignes[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Factures", n)
    c2.metric("Montant facturé (Ar)", f"{int(facture):,}".replace(",", " "))
    c3.metric("Montant remboursé (Ar)", f"{int(rembourse):,}".replace(",", " "))
    c4.metric("Rejetées", rejetees)
    statut = st.selectbox("Filtrer par statut",
                          ["Tous", "EN_COURS", "PAYEE", "REJETEE"])
    sql = """SELECT f.numero, a.pseudo, f.date_soins, f.categorie, f.prestataire,
                    f.montant_facture, f.montant_rembourse, f.statut, f.motif_rejet
             FROM factures_prov f JOIN assures_prov a ON a.id = f.assure_id"""
    if statut == "Tous":
        tableau(sql + " ORDER BY f.date_soins DESC")
    else:
        tableau(sql + " WHERE f.statut = %s ORDER BY f.date_soins DESC",
                (statut,))
    st.info("🚧 Les alertes de fraude (score, explications SHAP) seront "
            "branchées sur l'API de l'équipe.")


def etat_service(nom, test):
    try:
        test()
        st.success(f"{nom} : OK")
    except Exception as e:  # noqa: BLE001
        st.error(f"{nom} : indisponible ({type(e).__name__})")


def section_supervision():
    st.subheader("Supervision")
    periodes = {"1 heure": 1, "24 heures": 24, "7 jours": 168}
    choix = st.selectbox("Période", list(periodes))
    m = audit.metriques(periodes[choix])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Questions", m["questions"])
    c2.metric("Erreurs", m["erreurs"])
    c3.metric("Latence LLM moyenne",
              f"{m['latence_llm_ms'] / 1000:.1f} s")
    c4.metric("Latence p95", f"{m['p95_ms'] / 1000:.1f} s")
    c5, c6, c7 = st.columns(3)
    taux = (100 * m["cache"] / m["questions"]) if m["questions"] else 0
    c5.metric("Réponses du cache", f"{m['cache']} ({taux:.0f} %)")
    c6.metric("Demandes refusées (garde-fou)", m["refus"])
    c7.metric("Connexions échouées", m["connexions_echouees"])
    st.caption("Le journal ne conserve jamais le texte des questions "
               "(protection des données de santé).")
    with st.expander("Journal d'audit (30 derniers événements)"):
        tableau("""SELECT to_char(horodatage, 'YYYY-MM-DD HH24:MI:SS') AS horodatage,
                          login, role, evenement, detail, duree_ms, statut
                   FROM journal_audit ORDER BY id DESC LIMIT 30""")
    st.info("🚧 Le suivi de la dérive du modèle de fraude sera branché sur "
            "l'API de l'équipe.")


def page_admin(user):
    st.header("Administration")
    st.subheader("État des services")
    etat_service("Base de données PostgreSQL",
                 lambda: auth.requete("SELECT 1"))
    etat_service("Ollama (LLM)",
                 lambda: requests.get(f"{OLLAMA_URL}/api/tags",
                                      timeout=3).raise_for_status())
    _, l = auth.requete("SELECT COUNT(*) FROM documents_vectorises")
    st.write(f"Documents vectorisés : **{l[0][0]}**")

    section_supervision()

    st.subheader("Cache sémantique")
    _, l = auth.requete("SELECT COUNT(*), COALESCE(SUM(nb_hits),0) "
                        "FROM cache_semantique")
    c1, c2 = st.columns(2)
    c1.metric("Entrées en cache", l[0][0])
    c2.metric("Réponses servies par le cache", int(l[0][1]))
    _, s = auth.requete("SELECT valeur FROM parametres "
                        "WHERE cle = 'cache_seuil'")
    seuil = st.slider("Seuil de similarité (plus haut = plus strict)",
                      0.85, 0.99, float(s[0][0]) if s else 0.92, 0.01)
    col_a, col_b = st.columns(2)
    if col_a.button("Enregistrer le seuil"):
        conn = auth.connexion()
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO parametres VALUES ('cache_seuil', %s)
                           ON CONFLICT (cle) DO UPDATE SET valeur = EXCLUDED.valeur""",
                        (str(seuil),))
        conn.commit()
        conn.close()
        audit.journaliser(user["login"], user["role"], "config",
                          f"cache_seuil={seuil}")
        st.success(f"Seuil enregistré : {seuil} (effet immédiat)")
    if col_b.button("Vider le cache"):
        cache.vider()
        audit.journaliser(user["login"], user["role"], "config", "cache_vide")
        st.success("Cache vidé.")

    st.subheader("Utilisateurs")
    tableau("SELECT login, role, nom_affiche FROM utilisateurs_prov ORDER BY id")


PAGES = {
    "assure": [("Assistant virtuel", page_assistant),
               ("Mes factures", page_mes_factures)],
    "professionnel": [("Contrats, barème, réseau", page_pro)],
    "gestionnaire": [("Tableau de bord", page_gestionnaire)],
    "administrateur": [("Administration", page_admin),
                       ("Tableau de bord", page_gestionnaire)],
}


# --------------------------------------------------------------------
# Connexion et navigation
# --------------------------------------------------------------------
def ecran_login():
    st.title("🏥 PrediCare TPA")
    st.subheader("Connexion")
    if st.session_state.get("echecs", 0) >= 5:
        st.error("Trop de tentatives. Rechargez la page plus tard.")
        return
    with st.form("login"):
        login = st.text_input("Identifiant")
        mdp = st.text_input("Mot de passe", type="password")
        valider = st.form_submit_button("Se connecter")
    if valider:
        user = auth.verifier(login.strip(), mdp)
        if user:
            audit.journaliser(user["login"], user["role"], "connexion",
                              statut="ok")
            st.session_state["user"] = user
            st.session_state["echecs"] = 0
            st.rerun()
        audit.journaliser(login.strip(), None, "connexion", statut="echec")
        st.session_state["echecs"] = st.session_state.get("echecs", 0) + 1
        st.error("Identifiant ou mot de passe incorrect.")
    st.caption("Démo : assure1, assure2, assure3, pro1, gest1, admin1 "
               "(mot de passe de démonstration communiqué par l'équipe).")


def main():
    user = st.session_state.get("user")
    if not user:
        ecran_login()
        return
    with st.sidebar:
        st.write(f"**{user['nom']}**")
        st.caption(ROLES[user["role"]])
        pages = PAGES[user["role"]]
        choix = st.radio("Navigation", [p[0] for p in pages])
        if st.button("Se déconnecter"):
            st.session_state.clear()
            st.rerun()
    dict(pages)[choix](user)


main()
