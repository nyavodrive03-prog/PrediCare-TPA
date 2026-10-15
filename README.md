# PrediCare TPA

Plateforme de détection de fraude médicale – Projet Capstone

## Description

PrediCare TPA est une plateforme qui permet de :
- Détecter les fraudes sur les factures médicales (modèle XGBoost + SHAP)
- Stocker les prédictions
- Envoyer des alertes automatiques via n8n
- Gérer l’authentification avec 4 rôles

## Prérequis

Avant de commencer, installez :

- **Docker Desktop** (obligatoire)  
  → https://www.docker.com/products/docker-desktop/
- **Git**
- (Optionnel) Python 3.11 si vous voulez lancer des scripts hors Docker

## Structure du projet

```
PredicareTPA/
├── backend/                  # API FastAPI
├── data/
│   ├── raw/
│   │   ├── dataset/          # Les 12 CSV métier
│   │   ├── labels/           # labels_fraude.csv + labels_prestataires.csv
│   │   └── rag_corpus/       # PDF (pour plus tard)
│   └── processed/            # Fichiers générés par le feature engineering
├── ml/
│   └── models/               # Modèle entraîné (.pkl)
├── n8n/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Installation (sur un nouvel ordinateur)

### 1. Cloner le projet

```bash
git clone https://github.com/TON_USERNAME/PrediCare-TPA.git
cd PrediCare-TPA
```

### 2. Créer le fichier d’environnement

```bash
cp .env.example .env
```

### 3. Placer les données

Copiez vos fichiers CSV dans les bons dossiers :

- Les 12 fichiers CSV métier → `data/raw/dataset/`
- `labels_fraude.csv` et `labels_prestataires.csv` → `data/raw/labels/`

### 4. Lancer la plateforme

```bash
docker compose up --build -d
```

Attendez 30 à 60 secondes que tous les services démarrent.

### 5. Vérifier que tout fonctionne

Ouvrez votre navigateur :

| Service              | URL                          | Identifiants          |
|----------------------|------------------------------|-----------------------|
| API Documentation    | http://localhost:8000/docs   | -                     |
| Health Check         | http://localhost:8000/health | -                     |
| n8n                  | http://localhost:5679        | admin / admin123      |

## Comptes de test (Authentification)

| Rôle            | Username       | Password    |
|-----------------|----------------|-------------|
| Administrateur  | admin          | admin123    |
| Gestionnaire    | gestionnaire   | gest123     |
| Professionnel   | professionnel  | pro123      |
| Assuré          | assure         | assure123   |

## Endpoints principaux

### 1. Login
`POST /auth/login`

### 2. Prédiction de fraude
`POST /predict/`

Exemple de body :

```json
{
  "data": {
    "nb_lignes": 3,
    "montant_total": 125000,
    "a_ordonnance": 1,
    "ecart_tarif_moyen": 18000,
    "quantite_max": 3
  },
  "facture_id": "FAC-TEST-001"
}
```

### 3. Health Check
`GET /health`

## Recharger les données (si besoin)

Si la base est vide, lancez :

```bash
docker compose exec backend python load_data.py
```

Puis créez les utilisateurs :

```bash
docker compose exec backend python create_users.py
```

## Arrêter la plateforme

```bash
docker compose down
```

Pour tout supprimer (y compris les données) :

```bash
docker compose down -v
```

## Notes importantes

- Les fichiers de données (`data/raw/`) et le modèle (`ml/models/`) ne sont **pas** versionnés sur GitHub (trop lourds).
- Il faut donc les copier manuellement sur le nouvel ordinateur.
- Le port de n8n est **5679** (et non 5678) pour éviter les conflits.

## Auteurs

Équipe Capstone PrediCare TPA
