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

import auth  # noqa: E402
import cache  # noqa: E402
import garde_fous  # noqa: E402
from agent import agent as poser_question  # noqa: E402
from generation import repondre as repondre_documents  # noqa: E402

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


def afficher_chat(fonction, cle):
    """fonction(question) -> (texte, info). Garde l'historique en session."""
    historique = st.session_state.setdefault(cle, [])
    for m in historique:
        with st.chat_message(m["role"]):
            st.markdown(m["texte"])
            if m.get("info"):
                st.caption(m["info"])
    question = st.chat_input("Posez votre question...")
    if not question:
        return
    historique.append({"role": "user", "texte": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Je cherche la réponse..."):
            debut = time.time()
            try:
                texte, info = fonction(question)
                info = f"{info} · {time.time() - debut:.1f} s"
            except Exception as e:  # noqa: BLE001
                texte = ("Le service est momentanément indisponible. "
                         "Contactez PrediCare au 034 00 000 02.")
                info = f"Erreur technique : {type(e).__name__}"
        st.markdown(texte)
        st.caption(info)
    historique.append({"role": "assistant", "texte": texte, "info": info})


# --------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------
def page_assistant(user):
    st.header("Assistant virtuel")
    st.caption("Posez vos questions sur votre contrat ou vos remboursements.")

    def fn(q):
        # Garde-fou : refus avant tout appel à l'agent ou au LLM
        if garde_fous.vise_autre_assure(q, user["assure_id"]):
            return garde_fous.MESSAGE_REFUS, "🛡️ Demande refusée (aucune donnée lue)"
        res = poser_question(q, {"assure_id": user["assure_id"],
                                 "formule": user["formule"]})
        if res.get("cache"):
            info = f"⚡ Réponse du cache (similarité {res['similarite']})"
        else:
            noms = ", ".join(sorted({n for n, _ in res["outils"]})) or "aucun"
            info = f"🤖 Générée par le LLM · outils : {noms}"
        return res["reponse"], info

    afficher_chat(fn, "chat_assure")


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
        st.session_state["dernieres_sources"] = res["sources"]
        return res["reponse"], f"📄 Documents (formule {formule})"

    afficher_chat(fn, "chat_pro")
    sources = st.session_state.get("dernieres_sources")
    if sources:
        with st.expander("Passages utilisés pour la dernière réponse"):
            for i, s in enumerate(sources, 1):
                st.write(f"**[{i}]** {s['contenu']}")


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
        st.success(f"Seuil enregistré : {seuil} (effet immédiat)")
    if col_b.button("Vider le cache"):
        cache.vider()
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
            st.session_state["user"] = user
            st.session_state["echecs"] = 0
            st.rerun()
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