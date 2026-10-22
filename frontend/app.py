"""Interface web PrediCare TPA : login + parcours par rôle + BI."""
import json
import os
import sys
import time
import pandas as pd
import requests
import streamlit as st

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "rag"))
sys.path.insert(0, os.path.join(RACINE, "agent"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(RACINE, ".env"))

import auth  # noqa: E402
import garde_fous  # noqa: E402
from agent import agent as poser_question  # noqa: E402
from generation import repondre as repondre_documents  # noqa: E402

st.set_page_config(page_title="PrediCare TPA", page_icon="🏥", layout="wide")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
API_URL = os.getenv("API_URL", "http://backend:8000")

ROLES = {"assure": "Assuré", "professionnel": "Professionnel de santé",
         "gestionnaire": "Gestionnaire", "administrateur": "Administrateur"}

JSON_DEMO = """{
  "nb_lignes": 1, "montant_total": 86500, "montant_eligible": 80000,
  "reste_a_charge": 22500, "a_ordonnance": 0, "delai_soin_facture": 1,
  "delai_facture_reception": 16, "jour_semaine_soin": 0, "est_weekend": 0,
  "heure_soin_num": 10, "montant_moyen_ligne": 86500.0, "nb_lignes_reel": 1,
  "quantite_totale": 1, "quantite_max": 1, "prix_unitaire_max": 86500,
  "prix_unitaire_moyen": 86500.0, "montant_lignes_total": 86500,
  "nb_actes": 1, "nb_medicaments": 0, "diff_nb_lignes": 0, "ratio_medicaments": 0.0,
  "ecart_tarif_moyen": 0.0, "ecart_tarif_max": 0.0, "ecart_tarif_pct_moyen": 0.0,
  "nb_lignes_surfacturees": 0, "nb_lignes_avec_tarif": 0, "note_qualite": 4,
  "conventionne": 1, "type_prest_CABINET_DENTAIRE": false,
  "type_prest_CABINET_GENERALISTE": true, "niveau_TRES_ELEVE": true,
  "type_fac_CONSULTATION": true, "canal_PAPIER_SCAN": true, "mode_TIERS_PAYANT": true
}"""

def tableau(sql, params=None):
    colonnes, lignes = auth.requete(sql, params)
    st.dataframe([dict(zip(colonnes, l)) for l in lignes], use_container_width=True, hide_index=True)
    return lignes

def afficher_chat(fonction, cle):
    historique = st.session_state.setdefault(cle, [])
    for m in historique:
        with st.chat_message(m["role"]):
            st.markdown(m["texte"])
            if m.get("info"): st.caption(m["info"])
    question = st.chat_input("Posez votre question...")
    if not question: return
    historique.append({"role": "user", "texte": question})
    with st.chat_message("user"): st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Je cherche la réponse..."):
            debut = time.time()
            try:
                texte, info = fonction(question)
                info = f"{info} · {time.time() - debut:.1f} s"
            except Exception as e:
                texte = "Le service est momentanément indisponible."
                info = f"Erreur technique : {type(e).__name__}"
        st.markdown(texte)
        st.caption(info)
    historique.append({"role": "assistant", "texte": texte, "info": info})

# --- PAGES ---
def page_assistant(user):
    st.header("Assistant virtuel")
    def fn(q):
        if garde_fous.vise_autre_assure(q, user["assure_id"]):
            return garde_fous.MESSAGE_REFUS, "🛡️ Demande refusée"
        res = poser_question(q, {"assure_id": user["assure_id"], "formule": user["formule"]})
        info = "⚡ Cache" if res.get("cache") else "🤖 LLM"
        if res.get("outils") and res["outils"][0][0] == "RAG_Secours": info = "⚠️ Mode secours"
        return res["reponse"], info
    afficher_chat(fn, "chat_assure")

def page_mes_factures(user):
    st.header("Mes factures")
    tableau("""SELECT numero AS "N°", date_soins AS "Date", categorie AS "Catégorie",
               prestataire AS "Prestataire", montant_facture AS "Facturé",
               montant_rembourse AS "Remboursé", statut, motif_rejet 
               FROM factures_prov WHERE assure_id = %s ORDER BY date_soins DESC""", (user["assure_id"],))

def page_pro(user):
    st.header("Contrats, barème et réseau")
    formule = st.selectbox("Formule du patient", ["ESSENTIEL", "CONFORT", "PREMIUM"])
    def fn(q):
        res = repondre_documents(q, formule=formule)
        st.session_state["dernieres_sources"] = res["sources"]
        return res["reponse"], f"📄 Documents"
    afficher_chat(fn, "chat_pro")

def page_gestionnaire(user):
    st.header("Tableau de bord gestionnaire")
    _, lignes = auth.requete("""SELECT COUNT(*), COALESCE(SUM(montant_facture),0),
               COALESCE(SUM(montant_rembourse),0), COUNT(*) FILTER (WHERE statut = 'REJETEE') 
               FROM factures_prov""")
    n, facture, rembourse, rejetees = lignes[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Factures", n)
    c2.metric("Facturé (Ar)", f"{int(facture):,}".replace(",", " "))
    c3.metric("Remboursé (Ar)", f"{int(rembourse):,}".replace(",", " "))
    c4.metric("Rejetées", rejetees)
    
    st.divider()
    st.subheader("Analyser une facture (détection de fraude)")
    with st.expander("Tester une prédiction", expanded=True):
        json_input = st.text_area("JSON des features", height=200, value=JSON_DEMO)
        if st.button("Analyser la fraude", type="primary"):
            try:
                data = json.loads(json_input)
                response = requests.post(f"{API_URL}/predict/", json={"data": data},
                    headers={"Authorization": f"Bearer {user.get('token', '')}"}, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    score = result.get("score_fraude", 0)
                    if score >= 0.8: st.error(f"FRAUDE DÉTECTÉE – Score : {score}")
                    else: st.success(f"Facture normale – Score : {score}")
                    for exp in result.get("explication", []):
                        st.write(f"- **{exp['feature']}** → {exp['direction']}")
                else:
                    st.error(f"Erreur API : {response.status_code} – {response.text}")
            except Exception as e:
                st.error(f"Erreur : {e}")

def page_bi(user):
    st.header("Dashboard BI")
    cols, lignes = auth.requete("""SELECT f.date_soins, f.categorie, f.statut, 
               f.montant_facture, f.montant_rembourse, f.prestataire 
               FROM factures_prov f ORDER BY f.date_soins""")
    df = pd.DataFrame(lignes, columns=cols)
    if df.empty: return st.info("Aucune facture.")
    df["date_soins"] = pd.to_datetime(df["date_soins"])
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Facturé", f"{int(df['montant_facture'].sum()):,}".replace(",", " "))
    k2.metric("Total Remboursé", f"{int(df['montant_rembourse'].sum()):,}".replace(",", " "))
    k3.metric("Taux de Rejet", f"{(df['statut']=='REJETEE').mean()*100:.0f} %")
    
    st.bar_chart(df.groupby("categorie")[["montant_facture", "montant_rembourse"]].sum())
    st.download_button("Exporter CSV", df.to_csv(index=False).encode('utf-8'), "data.csv")

def page_admin(user):
    st.header("Administration")
    try:
        _, l = auth.requete("SELECT COUNT(*) FROM documents_vectorises")
        st.write(f"Documents vectorisés : **{l[0][0]}**")
    except Exception: st.warning("Table RAG introuvable.")
    tableau("SELECT username AS \"Identifiant\", role AS \"Rôle\" FROM users ORDER BY id")

PAGES = {
    "assure": [("Assistant virtuel", page_assistant), ("Mes factures", page_mes_factures)],
    "professionnel": [("Contrats, barème, réseau", page_pro)],
    "gestionnaire": [("Tableau de bord", page_gestionnaire), ("Dashboard BI", page_bi)],
    "administrateur": [("Administration", page_admin), ("Tableau de bord", page_gestionnaire), ("Dashboard BI", page_bi)],
}

def ecran_login():
    st.title("🏥 PrediCare TPA")
    with st.form("login"):
        login = st.text_input("Identifiant")
        mdp = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            user = auth.verifier(login.strip(), mdp)
            if user:
                st.session_state["user"] = user
                st.rerun()
            st.error("Identifiant ou mot de passe incorrect.")

def main():
    user = st.session_state.get("user")
    if not user: return ecran_login()
    with st.sidebar:
        st.write(f"**{user['nom']}**")
        st.caption(ROLES.get(user["role"], user["role"]))
        pages = PAGES.get(user["role"], [("Accueil", page_admin)])
        choix = st.radio("Navigation", [p[0] for p in pages])
        if st.button("Se déconnecter"):
            st.session_state.clear()
            st.rerun()
    dict(pages)[choix](user)

main()