Voici un **README.md** complet, clair et prêt à l’emploi pour lancer PrediCare sur un autre PC (Windows recommandé, car c’est l’environnement de développement actuel).

Tu peux le copier-coller directement dans un fichier `README.md` à la racine du projet.

---

```markdown
# PrediCare – Assistant TPA (Frontend + RAG + Agent)

Application d’assistance intelligente pour les professionnels et assurés TPA.  
Stack : Streamlit + PostgreSQL (pgvector) + Ollama + cache sémantique.

---

## Prérequis

| Logiciel              | Version minimale | Lien |
|-----------------------|------------------|------|
| Docker Desktop        | 4.x              | https://www.docker.com/products/docker-desktop/ |
| Ollama                | Dernière         | https://ollama.com/download |
| Git                   | 2.x              | https://git-scm.com |
| (Optionnel) Python 3.11+ | pour les scripts locaux | https://www.python.org |

> **Important** : Ollama doit rester installé **sur la machine hôte** (pas dans Docker).

---

## 1. Cloner le projet

```bash
git clone https://github.com/nyavodrive03-prog/PrediCare-TPA.git
cd PrediCare-TPA
git checkout Devsoa          # ou la branche qui contient le frontend
```

---

## 2. Préparer les données PDF

Les PDF ne sont **pas** versionnés dans Git (trop volumineux).

1. Crée le dossier :
   ```bash
   mkdir data\pdf
   ```
2. Place tous les PDF (baremes, contrats, garanties, médicaments, prestataires…) dans `data\pdf`.

---

## 3. Configuration (fichier `.env`)

Crée un fichier `.env` à la racine :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=predicare
DB_USER=postgres
DB_PASSWORD=test

CACHE_SEUIL=0.92
CACHE_TTL_HEURES=24
```

> En production, changez `DB_PASSWORD` et le mot de passe de démonstration `Demo2026!`.

---

## 4. Lancer avec Docker (recommandé)

### Première fois (construction + démarrage)

```bash
docker compose -f docker-compose.frontend.yml up -d --build
```

Attendez que les services soient `healthy` (environ 30-60 secondes) :

```bash
docker compose -f docker-compose.frontend.yml ps
```

### Démarrages suivants

```bash
docker compose -f docker-compose.frontend.yml up -d
```

### Arrêt propre

```bash
docker compose -f docker-compose.frontend.yml down
```

> **Ne jamais** utiliser `down -v` : cela efface les données de la base.

---

## 5. Initialisation des données (une seule fois)

Ouvre un terminal dans le dossier du projet et exécute les commandes suivantes **dans l’ordre** :

```bash
# 1. Créer les tables + charger les documents vectorisés (~1-2 min)
docker compose -f docker-compose.frontend.yml exec app python -m rag.ingestion

# 2. Créer les factures de démonstration
docker compose -f docker-compose.frontend.yml exec app python -m agent.seed_provisoire

# 3. Créer les 6 comptes de démonstration
docker compose -f docker-compose.frontend.yml exec app python -m frontend.seed_users
```

### Comptes de démonstration

| Identifiant | Rôle              | Mot de passe |
|-------------|-------------------|--------------|
| assure1     | Assuré            | Demo2026!    |
| assure2     | Assuré            | Demo2026!    |
| assure3     | Assuré            | Demo2026!    |
| pro1        | Professionnel     | Demo2026!    |
| gest1       | Gestionnaire      | Demo2026!    |
| admin1      | Administrateur    | Demo2026!    |

---

## 6. Accéder à l’application

Ouvre ton navigateur :

**http://localhost:8501**

- La première question est plus lente (chargement du modèle Ollama) → normal.
- Vérifie qu’Ollama tourne (icône dans la barre des tâches).

---

## 7. Commandes utiles

| Action                              | Commande |
|-------------------------------------|----------|
| Voir les logs                       | `docker compose -f docker-compose.frontend.yml logs -f` |
| Redémarrer la base                  | `docker start pgtest` (ou le nom du conteneur DB) |
| Vérifier le contenu de la base      | Voir section ci-dessous |
| Vider le cache sémantique           | Via l’écran Admin ou `python -m agent.cache` (fonction `vider`) |

### Contrôle rapide de la base

```bash
docker exec -it <nom_conteneur_db> psql -U postgres -d predicare -c "SELECT type, COUNT(*) FROM documents_vectorises GROUP BY type ORDER BY type;"
```

Résultat attendu :
```
 bareme      | 58
 contrat     | 42
 garantie    | 27
 medicament  | 28
 prestataire | 242
```

---

## 8. Développement local (sans Docker pour le frontend)

Si tu préfères lancer Streamlit en local :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Lancer PostgreSQL via Docker
docker compose -f docker-compose.frontend.yml up -d db

# Puis
streamlit run frontend/app.py
```

---

## 9. Structure du projet

```
PrediCare-TPA/
├── agent/                 # Agent + cache sémantique + garde-fous
├── frontend/              # Interface Streamlit
├── rag/                   # Ingestion + retrieval
├── data/pdf/              # PDF sources (non versionné)
├── docker-compose.frontend.yml
├── Dockerfile
├── requirements.txt
└── .env                   # À créer localement
```

---

## 10. Points d’attention

- Le conteneur PostgreSQL doit avoir `restart: unless-stopped` (déjà configuré).
- Les PDF doivent être fournis séparément à chaque nouvelle installation.
- Ollama reste sur l’hôte (pas containerisé pour le moment).
- Mot de passe de démo : `Demo2026!` — à changer en production.
- Mot de passe PostgreSQL par défaut : `test`.

---

## Support

En cas de problème :
1. Vérifie que Docker Desktop est bien démarré.
2. Vérifie qu’Ollama tourne.
3. Regarde les logs : `docker compose -f docker-compose.frontend.yml logs -f`

---

**Bonne utilisation !**  
PrediCare – Frontend + RAG + Agent
```

---

### Comment l’utiliser

1. Crée un fichier `README.md` à la racine de ton projet.
2. Colle le contenu ci-dessus.
3. Commit + push sur la branche `Devsoa` (ou celle que tu utilises).

Tu veux que je te génère aussi une version plus courte (juste les commandes essentielles) ou une version en anglais ?
