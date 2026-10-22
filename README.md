# 🏥 PrediCare TPA — Plateforme Intelligente de Gestion et de Détection de Fraude

Bienvenue sur le dépôt officiel de **PrediCare TPA**.

PrediCare TPA est une plateforme Data End-to-End conçue pour automatiser le contrôle des factures médicales, détecter les anomalies financières et faciliter l'analyse des fraudes grâce au Machine Learning et à l'explicabilité SHAP.

La plateforme intègre également un assistant conversationnel basé sur le RAG (Retrieval-Augmented Generation), une base de données PostgreSQL avec pgvector, un système d'authentification par JWT et un mécanisme d'alertes automatisées via n8n.

## 📋 Table des matières

1. [Présentation du projet](#-présentation-du-projet)
2. [Architecture technique](#-architecture-technique)
3. [Prérequis](#1-prérequis)
4. [Installation du projet](#2-installation-du-projet)
5. [Configuration de l'environnement](#3-configuration-de-lenvironnement)
6. [Lancement de l'infrastructure](#4-lancement-de-linfrastructure)
7. [Initialisation des données et de la base](#5-initialisation-des-données-et-de-la-base)
8. [Pipeline Machine Learning](#6-pipeline-machine-learning)
9. [Configuration du workflow n8n](#7-configuration-du-workflow-n8n)
10. [Vérifications et tests](#8-vérifications-et-tests)
11. [Comptes de test et rôles](#9-comptes-de-test-et-rôles)
12. [Commandes utiles](#10-commandes-utiles)
13. [Dépannage](#11-dépannage)

---

## 🎯 Présentation du projet

PrediCare TPA répond à plusieurs besoins liés à la gestion des prestations d'assurance santé.

### Fonctionnalités principales

- **Gestion des factures médicales** : chargement et exploitation des données métier.
- **Détection de fraude** : identification des factures présentant des caractéristiques suspectes.
- **Machine Learning** : utilisation d'un modèle XGBoost pour estimer le risque de fraude.
- **Explicabilité SHAP** : identification des variables qui contribuent aux prédictions du modèle.
- **Dashboard BI** : visualisation des indicateurs métier, des montants et de leur évolution.
- **Assistant conversationnel RAG** : recherche d'informations dans les documents PDF de référence.
- **Authentification sécurisée** : connexion des utilisateurs et gestion des accès selon leurs rôles.
- **Alertes automatisées** : transmission des alertes de fraude à un workflow n8n.
- **Base de données vectorielle** : utilisation de pgvector pour la recherche sémantique dans les documents.

### Objectifs

Le projet vise à :

1. Centraliser les données relatives aux assurés, aux contrats et aux factures.
2. Automatiser les contrôles de cohérence.
3. Détecter les anomalies financières.
4. Expliquer les prédictions du modèle.
5. Fournir des outils de visualisation et d'aide à la décision.
6. Faciliter l'accès aux informations contractuelles grâce à un assistant conversationnel.

---

## 🏗️ Architecture technique

L'application repose sur une architecture composée de plusieurs services.

| Composant | Technologie | Fonction |
|---|---|---|
| Backend | Python | Traitement des données et logique métier |
| API | Selon l'implémentation du projet | Exposition des fonctionnalités backend |
| Frontend | Streamlit | Interface utilisateur et tableaux de bord |
| Base de données | PostgreSQL | Stockage des données métier |
| Recherche vectorielle | pgvector | Stockage et recherche des embeddings |
| Machine Learning | XGBoost | Prédiction du risque de fraude |
| Explicabilité | SHAP | Interprétation des prédictions |
| Assistant documentaire | RAG | Recherche dans les documents PDF |
| Modèle de langage | Ollama, optionnel | Génération des réponses de l'assistant |
| Automatisation | n8n | Gestion des alertes |
| Conteneurisation | Docker Compose | Déploiement des services |

**Remarque :** les technologies et les noms de services doivent correspondre aux fichiers réellement présents dans le dépôt.

---

## 1. Prérequis

Avant de commencer, installez les outils nécessaires sur votre ordinateur.

### 1.1. Docker Desktop

Docker permet de lancer les différents composants de l'application dans des conteneurs.

Téléchargement :
https://www.docker.com/products/docker-desktop/

Après l'installation, vérifiez que Docker fonctionne :

```bash
docker --version
docker compose version
```

### 1.2. Git

Git permet de récupérer le code source du projet.

Téléchargement :
https://git-scm.com/

Vérification :

```bash
git --version
```

### 1.3. Ollama (optionnel)

Ollama permet d'exécuter un modèle de langage local pour compléter les fonctionnalités de l'assistant conversationnel.

Téléchargement :
https://ollama.com/

Il est possible de lancer la plateforme sans Ollama si le projet prévoit un mode de secours pour l'assistant.

---

## 2. Installation du projet

### 2.1. Cloner le dépôt

Ouvrez un terminal et exécutez les commandes suivantes en remplaçant l'URL d'exemple par celle du dépôt réel.

```bash
git clone https://github.com/VOTRE_REPO/PrediCare-TPA.git
cd PrediCare-TPA
```

**Important :** `VOTRE_REPO` est un espace réservé. Il doit être remplacé par l'adresse réelle du dépôt GitHub.

### 2.2. Vérifier la structure du projet

Avant de lancer les services, vérifiez que les fichiers nécessaires sont présents.

```text
PrediCare-TPA/
├── backend/
├── frontend/
├── data/
│   ├── raw/
│   │   ├── dataset/
│   │   └── labels/
│   └── pdf/
├── ml/
│   └── models/
├── n8n/
├── docker-compose.yml
├── .env.example
└── README.md
```

Cette arborescence est indicative. Les chemins réels dépendent de l'organisation du dépôt.

Vérifiez notamment la présence des fichiers suivants, s'ils sont utilisés par votre version du projet :

- `docker-compose.yml` ou `compose.yaml`
- `.env.example`
- `load_data.py`
- `create_users.py`
- `prepare_data.py`
- `feature_engineering_v1.py`
- `feature_engineering_v2.py`
- `feature_engineering_v3.py`
- `prepare_final_dataset.py`
- `train_model.py`
- `n8n/workflow-fraude-alerte.json`

Ne créez pas de fichiers factices portant ces noms : vérifiez leur présence et leur emplacement dans le dépôt.

### 2.3. Ajouter les données brutes

Les fichiers volumineux ne sont pas nécessairement versionnés sur Git.

Si les données ne sont pas incluses dans le dépôt, récupérez-les depuis la source autorisée du projet.

Placez ensuite les fichiers dans les répertoires attendus par les scripts.

#### Données métier

Répertoire prévu :

```text
data/raw/dataset/
```

Ce répertoire doit contenir les fichiers CSV métier nécessaires au chargement des données.

Exemples de noms de fichiers :

- `assures.csv`
- `factures.csv`
- `lignes_facture.csv`

La liste exacte dépend du dataset utilisé.

#### Fichiers de labels

Répertoire prévu :

```text
data/raw/labels/
```

Exemples :

- `labels_fraude.csv`
- `labels_prestataires.csv`

Vérifiez les noms et les colonnes attendus par les scripts de préparation.

#### Documents PDF

Répertoire prévu :

```text
data/pdf/
```

Ce répertoire doit contenir les documents de référence utilisés par l'assistant RAG.

Exemples :

- `Bareme_Reference_Actes.pdf`
- `Conditions_Generales_CONFORT.pdf`

Vérifiez que les noms des fichiers correspondent à ceux attendus par le code d'ingestion.

**Attention :** les noms et les nombres de fichiers indiqués dans cette section sont des exemples issus de la configuration documentaire du projet. Ils doivent être confirmés à partir des fichiers réellement fournis.

---

## 3. Configuration de l'environnement

### 3.1. Créer le fichier `.env`

À la racine du projet, copiez le fichier d'exemple :

```bash
cp .env.example .env
```

Sous Windows, vous pouvez également copier le fichier avec PowerShell :

```powershell
Copy-Item .env.example .env
```

Si `.env.example` n'existe pas, recherchez les instructions de configuration du dépôt avant de créer manuellement les variables.

### 3.2. Configurer les variables

Ouvrez `.env` et renseignez les paramètres nécessaires aux services.

Les variables peuvent notamment concerner :

- les identifiants PostgreSQL ;
- le port exposé par la base de données ;
- les secrets JWT ;
- les identifiants de connexion n8n ;
- les paramètres de connexion à Ollama ;
- les autres paramètres requis par le backend et le frontend.

Les noms exacts des variables dépendent des fichiers de configuration du projet.

### 3.3. Vérifier les ports

La configuration prévue dans ce projet utilise notamment les ports suivants :

| Service | Port local indicatif |
|---|---:|
| API backend | 8000 |
| Frontend Streamlit | 8501 |
| Interface n8n | 5679 |
| PostgreSQL | 5433 |

Ces ports doivent être vérifiés dans le fichier Compose.

Si PostgreSQL utilise le port hôte `5433`, cela signifie généralement que le port `5433` de l'ordinateur est redirigé vers le port `5432` du conteneur.

À l'intérieur du réseau Docker, les services communiquent généralement avec PostgreSQL sur le port `5432`, en utilisant le nom du service comme hôte.

Ne supposez pas que les ports indiqués sont actifs tant que la configuration Docker n'a pas été vérifiée.

**Sécurité :**

- Ne partagez pas votre fichier `.env`.
- Ne publiez pas de mots de passe ou de secrets JWT sur GitHub.
- Utilisez des secrets appropriés en environnement de production.
- Changez les identifiants par défaut avant tout déploiement public.

---

## 4. Lancement de l'infrastructure

### 4.1. Construire et démarrer les services

Depuis la racine du projet, exécutez :

```bash
docker compose up -d --build
```

Cette commande demande à Docker Compose de construire les images nécessaires et de démarrer les services définis dans le fichier Compose.

La première construction peut prendre plusieurs minutes.

### 4.2. Vérifier l'état des conteneurs

```bash
docker compose ps
```

Vérifiez que les services attendus sont démarrés.

Selon leur configuration, les services peuvent apparaître avec les états `Up`, `running` ou `healthy`.

Un conteneur démarré n'est pas nécessairement prêt à traiter des requêtes. Consultez les journaux si un service ne répond pas.

### 4.3. Consulter les journaux

Pour consulter les journaux de tous les services :

```bash
docker compose logs
```

Pour suivre les journaux en continu :

```bash
docker compose logs -f
```

Pour consulter uniquement le backend :

```bash
docker compose logs -f backend
```

Pour consulter uniquement le frontend :

```bash
docker compose logs -f frontend
```

Les noms `backend` et `frontend` doivent correspondre aux noms des services déclarés dans le fichier Compose.

### 4.4. Accéder aux interfaces

Si les ports indiqués sont correctement configurés, les interfaces peuvent être accessibles aux adresses suivantes :

- Frontend : http://localhost:8501
- API : http://localhost:8000
- n8n : http://localhost:5679

Ces URL ne seront accessibles que si les services correspondants sont configurés, démarrés et exposent bien les ports attendus.

---

## 5. Initialisation des données et de la base

Une fois les conteneurs démarrés, initialisez la base de données et les composants nécessaires.

Les commandes ci-dessous correspondent à l'organisation envisagée pour le projet. Vérifiez la présence des scripts et leurs dépendances avant de les exécuter.

### 5.1. Charger les données métier

Si le script `load_data.py` se trouve à la racine du backend et que le service est correctement configuré, exécutez :

```bash
docker compose exec backend python load_data.py
```

Ce script est prévu pour charger les données métier dans PostgreSQL.

Selon son implémentation, il peut :

- créer les tables ;
- lire les fichiers CSV ;
- transformer les données ;
- insérer les enregistrements dans la base.

Le nombre de tables et d'enregistrements dépend du dataset et de la version du script.

Vérifiez les messages affichés dans le terminal pour confirmer le bon déroulement du chargement.

### 5.2. Créer les utilisateurs

Si `create_users.py` est disponible dans le conteneur backend :

```bash
docker compose exec backend python create_users.py
```

Ce script est prévu pour initialiser les comptes de test.

Vérifiez son contenu avant de l'exécuter afin de connaître les comptes créés et les éventuelles règles de gestion des mots de passe.

### 5.3. Indexer les documents pour le RAG

Si le module `rag.ingestion` se trouve dans le conteneur frontend :

```bash
docker compose exec frontend python -m rag.ingestion
```

Le processus d'ingestion peut notamment :

1. Lire les documents PDF.
2. Extraire leur contenu textuel.
3. Découper le texte en passages.
4. Générer des embeddings.
5. Stocker les vecteurs dans PostgreSQL via pgvector.

Le succès de cette étape dépend également de la disponibilité du modèle d'embeddings et de la configuration de la base de données.

Vérifiez les journaux afin de confirmer que les documents ont été traités.

### 5.4. Initialiser les tables de l'agent IA

Si le module `agent.seed_provisoire` existe dans le conteneur frontend :

```bash
docker compose exec frontend python -m agent.seed_provisoire
```

Cette commande est prévue pour initialiser les données ou les tables nécessaires à l'agent IA.

Vérifiez le code du module pour connaître les opérations réellement effectuées.

### 5.5. Vérifier la base de données

Après l'initialisation :

- vérifiez que les tables attendues existent ;
- confirmez que les données métier sont présentes ;
- vérifiez que les utilisateurs ont été créés ;
- contrôlez la présence des données vectorielles si le RAG est activé.

Ne lancez pas plusieurs fois les scripts d'initialisation sans vérifier leur comportement. Certains scripts sont idempotents, tandis que d'autres peuvent dupliquer les données ou échouer si les tables existent déjà.

---

## 6. Pipeline Machine Learning

Cette section décrit la séquence de préparation des données et d'entraînement du modèle de détection de fraude.

**Important :** l'ordre ci-dessous correspond au pipeline envisagé pour le projet. Vérifiez les dépendances entre les scripts avant de régénérer les datasets ou le modèle.

### 6.1. Vue d'ensemble

Le pipeline comprend les étapes suivantes :

1. Fusion des données métier et des labels.
2. Première phase de Feature Engineering.
3. Deuxième phase de Feature Engineering.
4. Troisième phase de Feature Engineering.
5. Construction du dataset final.
6. Entraînement du modèle XGBoost.

### 6.2. Étape 1 — Préparer les données

Si le script `prepare_data.py` existe dans le conteneur backend :

```bash
docker compose exec backend python prepare_data.py
```

Cette étape est prévue pour préparer les données nécessaires à l'entraînement, notamment en reliant les factures aux labels de fraude.

Vérifiez les fichiers produits et les colonnes disponibles.

### 6.3. Étape 2 — Feature Engineering v1

```bash
docker compose exec backend python feature_engineering_v1.py
```

Cette étape peut notamment créer des variables relatives :

- aux délais ;
- aux dates ;
- aux jours de la semaine ;
- aux week-ends ;
- aux horaires.

Les variables réellement créées dépendent de l'implémentation du script.

### 6.4. Étape 3 — Feature Engineering v2

```bash
docker compose exec backend python feature_engineering_v2.py
```

Cette étape est prévue pour enrichir les données avec des informations issues des lignes de facture.

Les variables peuvent notamment concerner les actes, les quantités ou les montants, selon les données disponibles.

### 6.5. Étape 4 — Feature Engineering v3

```bash
docker compose exec backend python feature_engineering_v3.py
```

Cette étape peut enrichir les données avec des variables relatives :

- aux tarifs ;
- aux prestataires ;
- aux écarts par rapport aux références ;
- aux caractéristiques agrégées des factures.

Vérifiez les transformations réellement appliquées.

### 6.6. Étape 5 — Construire le dataset final

```bash
docker compose exec backend python prepare_final_dataset.py
```

Cette étape est prévue pour consolider les variables calculées et produire le dataset final d'entraînement.

Vérifiez notamment :

- le nombre de lignes ;
- la présence de la variable cible ;
- les valeurs manquantes ;
- les doublons ;
- les colonnes utilisées comme variables explicatives.

### 6.7. Étape 6 — Entraîner le modèle

```bash
docker compose exec backend python train_model.py
```

Ce script est prévu pour entraîner le modèle de détection de fraude.

Selon son implémentation, il peut intégrer :

- un modèle XGBoost ;
- un traitement du déséquilibre des classes ;
- SMOTE ;
- une séparation entre les données d'entraînement et de test ;
- des métriques de performance ;
- des explications SHAP ;
- la sauvegarde des artefacts du modèle.

L'utilisation effective de ces techniques doit être confirmée dans le code du script.

### 6.8. Vérifier les artefacts

Le projet prévoit notamment les fichiers suivants :

```text
ml/
└── models/v1
            ├── fraud_model_xgb.pkl
            └── feature_names.pkl
```

Ces noms et ce chemin sont à confirmer dans la configuration du modèle.

Si les fichiers ne sont pas présents après l'entraînement :

1. Consultez les journaux du script.
2. Vérifiez le chemin de sortie configuré.
3. Vérifiez les permissions du répertoire.
4. Assurez-vous que l'entraînement s'est terminé sans erreur.

**Attention aux fuites de données :** les transformations apprises à partir des données doivent être ajustées sur les données d'entraînement uniquement. Si SMOTE est utilisé, il doit être appliqué à l'ensemble d'entraînement, et non à l'ensemble de test.

---

## 7. Configuration du workflow n8n

n8n permet d'automatiser le traitement des alertes de fraude.

Dans la configuration envisagée, une alerte est déclenchée lorsque le score de fraude dépasse un seuil défini.

### 7.1. Ouvrir n8n

Si le service est accessible sur le port configuré :

http://localhost:5679

Connectez-vous avec les identifiants définis dans votre configuration.

Ne supposez pas que les identifiants par défaut sont actifs. Consultez le fichier `.env` et la configuration du service.

### 7.2. Importer le workflow

Le projet prévoit le fichier suivant :

```text
n8n/workflow-fraude-alerte.json
```

Dans l'interface n8n :

1. Ouvrez le menu des workflows.
2. Choisissez l'option d'importation depuis un fichier.
3. Sélectionnez le fichier JSON.
4. Vérifiez les nœuds et les paramètres.
5. Enregistrez le workflow.

Si le fichier n'existe pas, il faut le récupérer auprès de l'équipe du projet ou vérifier le chemin réel du workflow.

### 7.3. Vérifier le webhook

Le workflow envisagé utilise un webhook :

- Méthode HTTP : `POST`
- Chemin : `fraude-alerte`

Ces paramètres doivent être confirmés dans le workflow importé.

Le backend doit envoyer les données au webhook correspondant.

### 7.4. Vérifier la condition de fraude

Le seuil envisagé est de `0.8`.

La condition logique est :

```text
score_fraude > 0.8
```

Si le workflow reçoit un corps JSON contenant un objet `score_fraude`, une expression possible dans un nœud IF est :

```javascript
{{ $json.body.score_fraude > 0.8 }}
```

L'expression exacte dépend de la structure réelle des données reçues.

### 7.5. Activer le workflow

Après vérification :

1. Testez le webhook avec une requête contrôlée.
2. Vérifiez les données reçues.
3. Contrôlez le résultat du nœud IF.
4. Activez ou publiez le workflow selon la version de n8n.

Ne transmettez pas de véritables données médicales ou personnelles pendant les tests si des données synthétiques suffisent.

---

## 8. Vérifications et tests

Cette section propose une checklist pour vérifier les principales fonctionnalités avant une démonstration.

Les URL, comptes et résultats attendus doivent être adaptés à la configuration réellement déployée.

### 8.1. Vérifier l'état des services

```bash
docker compose ps
```

Vérifiez que les conteneurs attendus sont démarrés.

En cas d'erreur :

```bash
docker compose logs --tail=100
```

### 8.2. Tester l'API

Si le backend expose une route de santé sur `/health` :

```bash
curl http://localhost:8000/health
```

La réponse attendue dépend de l'implémentation.

Si cette route n'existe pas, consultez la documentation de l'API ou le code du backend pour trouver la route de vérification correcte.

### 8.3. Tester l'authentification

Si l'API utilise une route de connexion compatible avec le formulaire suivant :

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Cette commande est un exemple de requête HTTP.

Elle ne doit être utilisée qu'après vérification de la route, du format attendu et de l'existence du compte de test.

Une authentification réussie peut retourner un jeton JWT, selon l'implémentation.

### 8.4. Tester le frontend

Ouvrez l'adresse suivante si le frontend est exposé sur le port 8501 :

http://localhost:8501

Connectez-vous avec un compte de test valide.

#### Test 1 — Dashboard BI

Vérifiez :

- l'affichage des indicateurs ;
- les graphiques de répartition ;
- l'évolution des montants ;
- les filtres disponibles ;
- l'export CSV, s'il est implémenté.

#### Test 2 — Détection de fraude

Vérifiez :

- la possibilité de sélectionner une facture ;
- le déclenchement de l'analyse ;
- l'affichage du score de fraude ;
- la présentation des variables explicatives ;
- l'affichage des explications SHAP, si elles sont intégrées.

Un score élevé ne constitue pas, à lui seul, une preuve de fraude. Il s'agit d'un indicateur à examiner dans son contexte métier.

#### Test 3 — Assistant conversationnel RAG

Vérifiez :

- que les documents ont été indexés ;
- que l'assistant accepte une question ;
- que les passages pertinents sont retrouvés ;
- que les réponses s'appuient sur les documents disponibles ;
- que les droits d'accès aux données sont respectés.

Exemple de question :

« Quel est mon taux de remboursement pour une consultation ? »

La réponse doit dépendre des documents et des données réellement disponibles dans la base.

#### Test 4 — Gestion des rôles

Connectez-vous successivement avec les comptes de test prévus.

Vérifiez que chaque utilisateur ne peut accéder qu'aux fonctionnalités autorisées par son rôle.

#### Test 5 — Alertes n8n

Envoyez une requête de test au webhook.

Vérifiez :

- la réception du JSON ;
- la lecture du score ;
- l'évaluation de la condition ;
- l'exécution de la branche appropriée.

Utilisez des données fictives pour ces tests.

### 8.5. Checklist finale

Avant la démonstration, confirmez les points suivants :

- [ ] Le dépôt est disponible localement.
- [ ] Les fichiers de données requis sont présents.
- [ ] Le fichier `.env` est configuré.
- [ ] Les services Docker sont démarrés.
- [ ] La base de données est accessible.
- [ ] Les données métier sont chargées.
- [ ] Les comptes de test existent.
- [ ] Les documents PDF ont été indexés.
- [ ] Les artefacts du modèle sont disponibles.
- [ ] Le backend répond aux requêtes attendues.
- [ ] Le frontend est accessible.
- [ ] Le Dashboard BI fonctionne.
- [ ] La détection de fraude fonctionne.
- [ ] Les explications SHAP sont disponibles si prévues.
- [ ] L'assistant RAG répond aux questions.
- [ ] Les permissions sont correctement appliquées.
- [ ] Le workflow n8n a été testé.
- [ ] Aucun secret n'est exposé dans le dépôt.

---

## 9. Comptes de test et rôles

Le tableau ci-dessous reprend les comptes de démonstration prévus dans la configuration initiale du projet.

**Important :** ces comptes ne sont pas garantis. Ils doivent être confirmés dans le script d'initialisation des utilisateurs ou dans la configuration réelle de l'application.

| Rôle | Identifiant indicatif | Mot de passe indicatif | Accès prévu |
|---|---|---|---|
| Administrateur | `admin` | `admin123` | Administration et gestion des utilisateurs |
| Gestionnaire | `gestionnaire` | `gest123` | Tableau de bord et détection de fraude |
| Professionnel | `professionnel` | `pro123` | Consultation des contrats et des informations autorisées |
| Assuré | `assure` | `assure123` | Assistant virtuel et consultation de ses propres informations |

Ces identifiants sont réservés à un environnement de test local.

Ne réutilisez pas ces mots de passe en production.

Les permissions réelles doivent être contrôlées dans le code de l'authentification et de l'autorisation.

---

## 10. Commandes utiles

### 10.1. Docker Compose

| Action | Commande |
|---|---|
| Construire et démarrer les services | `docker compose up -d --build` |
| Afficher les conteneurs | `docker compose ps` |
| Afficher les journaux | `docker compose logs` |
| Suivre les journaux | `docker compose logs -f` |
| Suivre les journaux du backend | `docker compose logs -f backend` |
| Suivre les journaux du frontend | `docker compose logs -f frontend` |
| Redémarrer le backend | `docker compose restart backend` |
| Redémarrer le frontend | `docker compose restart frontend` |
| Arrêter les services | `docker compose down` |

Les noms des services doivent correspondre au fichier Compose.

### 10.2. Reconstruire un service

Pour reconstruire un service après une modification de son code ou de ses dépendances :

```bash
docker compose build backend
```

Puis redémarrez le service :

```bash
docker compose up -d backend
```

Adaptez le nom du service à celui déclaré dans le fichier Compose.

### 10.3. Arrêter et supprimer les conteneurs

```bash
docker compose down
```

Cette commande arrête les services et supprime les conteneurs et réseaux gérés par Compose.

Les volumes persistants ne sont normalement pas supprimés par cette commande.

### 10.4. Supprimer également les volumes

```bash
docker compose down -v
```

**Attention : cette commande peut supprimer les volumes contenant la base de données et d'autres données persistantes.**

Ne l'utilisez pas si vous souhaitez conserver les données.

Avant toute suppression, vérifiez les volumes déclarés dans le fichier Compose et effectuez une sauvegarde si nécessaire.

---

## 11. Dépannage

### 11.1. Erreur : `port is already allocated`

Cette erreur indique généralement qu'un autre processus utilise déjà un port requis.

Vérifiez les ports exposés dans le fichier Compose et identifiez le service qui les utilise.

Sous Linux :

```bash
sudo lsof -i :8000
```

Pour vérifier un autre port, remplacez `8000` par le numéro concerné.

Sous Windows PowerShell :

```powershell
netstat -ano | findstr :8000
```

Ne terminez pas un processus sans avoir vérifié son rôle.

Si le port est déjà utilisé par une application nécessaire, vous pouvez modifier le port hôte dans le fichier Compose, puis redémarrer les services.

### 11.2. Erreur : `ModuleNotFoundError`

Cette erreur indique généralement qu'un module Python n'est pas disponible dans l'environnement d'exécution.

Vérifiez :

1. Que le module est déclaré dans le fichier de dépendances approprié.
2. Que le service utilise le bon environnement Python.
3. Que le fichier de dépendances est bien installé dans l'image Docker.
4. Que le module est importé avec le bon chemin.

Après correction, reconstruisez le service concerné.

Exemple :

```bash
docker compose build backend
docker compose up -d backend
```

### 11.3. La base de données est vide

Vérifiez :

- que PostgreSQL est démarré ;
- que les variables de connexion sont correctes ;
- que les fichiers CSV sont disponibles ;
- que le script de chargement s'est terminé correctement ;
- que le backend pointe vers la bonne base ;
- que les données n'ont pas été chargées dans une autre instance PostgreSQL.

Consultez les journaux :

```bash
docker compose logs --tail=100 backend
```

Si nécessaire, relancez le chargement uniquement après avoir vérifié si le script peut être exécuté plusieurs fois sans produire de doublons.

### 11.4. L'assistant RAG ne répond pas

Vérifiez les éléments suivants :

- les fichiers PDF sont présents ;
- l'ingestion s'est terminée sans erreur ;
- les embeddings ont été générés ;
- pgvector est disponible ;
- les documents indexés sont accessibles ;
- le frontend utilise la bonne configuration de connexion ;
- le modèle de langage est accessible si la génération dépend d'Ollama.

Si le projet prévoit un mode de secours, l'assistant peut retourner des passages documentaires sans produire de réponse rédigée par un modèle de langage.

Pour utiliser Ollama, installez-le depuis :

https://ollama.com/

Puis téléchargez un modèle compatible avec votre configuration.

Exemple :

```bash
ollama pull llama3
```

Le nom du modèle doit correspondre à celui configuré dans l'application.

Si le conteneur frontend doit communiquer avec Ollama installé sur l'hôte, vérifiez l'adresse réseau utilisée par le conteneur. `localhost` à l'intérieur d'un conteneur désigne généralement le conteneur lui-même, et non l'ordinateur hôte.

Après toute modification de configuration :

```bash
docker compose restart frontend
```

### 11.5. Le modèle de fraude ne se charge pas

Vérifiez :

- que le fichier du modèle existe ;
- que le chemin de chargement correspond au chemin de sauvegarde ;
- que le conteneur peut lire le fichier ;
- que les bibliothèques nécessaires sont installées ;
- que le modèle a été entraîné avec une version compatible des dépendances.

Vérifiez également que les variables d'entrée du modèle correspondent aux variables utilisées lors de l'entraînement.

### 11.6. Les explications SHAP ne s'affichent pas

Vérifiez :

- que SHAP est installé dans l'environnement approprié ;
- que le modèle est correctement chargé ;
- que les données fournies à SHAP ont le bon format ;
- que les noms des variables correspondent aux données d'entraînement ;
- que le code de visualisation est exécuté sans erreur.

Consultez les journaux du service concerné pour identifier l'origine du problème.

### 11.7. Le workflow n8n ne reçoit aucune alerte

Vérifiez :

- que le workflow est activé ;
- que le webhook est correctement configuré ;
- que l'URL utilisée par le backend est accessible depuis son conteneur ;
- que la méthode HTTP correspond à celle attendue ;
- que la structure du JSON correspond aux expressions du workflow ;
- que le champ `score_fraude` est présent et numérique.

Un webhook utilisant `localhost` depuis un autre conteneur peut pointer vers le mauvais service. Utilisez le nom réseau du service lorsque la configuration Docker le nécessite.

---

## 🔐 Bonnes pratiques de sécurité

Pour toute utilisation au-delà d'une démonstration locale :

- Remplacez les identifiants de test.
- Utilisez des secrets robustes.
- Ne versionnez jamais `.env`.
- Limitez les accès aux données médicales et personnelles.
- Vérifiez les permissions associées aux rôles.
- Protégez les routes de l'API.
- Évitez d'exposer directement PostgreSQL sur Internet.
- Limitez les informations sensibles inscrites dans les journaux.
- Utilisez des données synthétiques lorsque cela est possible.
- Vérifiez les autorisations avant d'indexer des documents dans le système RAG.
- Contrôlez les réponses de l'assistant pour éviter la divulgation de données auxquelles l'utilisateur n'a pas accès.
- Sauvegardez la base de données avant les opérations destructives.

---

## 📌 Informations importantes

Ce README décrit le processus d'installation et d'exploitation prévu pour PrediCare TPA.

Les commandes, noms de scripts, chemins, ports, comptes de test et fonctionnalités doivent être vérifiés par rapport à la version réelle du dépôt.

En particulier :

- Le nom du dépôt GitHub doit être remplacé par son URL réelle.
- Les fichiers de données doivent provenir de la source prévue pour le projet.
- Les noms des services Docker doivent correspondre au fichier Compose.
- Les scripts doivent exister dans les conteneurs aux emplacements indiqués.
- Les routes de l'API doivent être confirmées dans le backend.
- Les comptes de test doivent être confirmés dans le script de création des utilisateurs.
- Le workflow n8n doit être vérifié avant son activation.
- Les résultats du modèle doivent être évalués sur des données adaptées.

---

## 👥 Équipe et crédits

**Projet :** PrediCare TPA
**Domaine :** Data Engineering, Machine Learning et Intelligence Artificielle
**Objectif :** gestion des factures médicales, détection des anomalies et assistance documentaire.

Développé dans le cadre du projet Capstone PrediCare TPA — Cohorte IA, ODC & Ingedata.