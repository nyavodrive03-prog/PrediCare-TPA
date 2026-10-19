# PrediCare TPA

Plateforme de détection de fraude médicale – Projet Capstone

Ce guide permet de **tout reconstruire depuis zéro** sur un nouvel ordinateur  
(jusqu’aux alertes n8n), sans copier le modèle déjà entraîné.

---

## 1. Prérequis

- Docker Desktop (obligatoire) → https://www.docker.com/products/docker-desktop/
- Git

Docker doit être démarré avant de continuer.

---

## 2. Cloner le projet

```bash
git clone https://github.com/TON_USERNAME/PrediCare-TPA.git
cd PrediCare-TPA
```

---

## 3. Placer uniquement les données brutes

Copiez **seulement** les fichiers sources (ne copiez pas le modèle ni les fichiers processed) :

```
data/raw/dataset/          ← les 12 fichiers CSV métier
data/raw/labels/           ← labels_fraude.csv + labels_prestataires.csv
```

---

## 4. Configuration

```bash
cp .env.example .env
```

---

## 5. Lancer l’infrastructure

```bash
docker compose up --build -d
```

Attendez 40 à 60 secondes.

### Vérifications

| Service        | URL                          |
|----------------|------------------------------|
| Health Check   | http://localhost:8000/health |
| Documentation  | http://localhost:8000/docs   |
| n8n            | http://localhost:5679        |

---

## 6. Charger les données dans PostgreSQL

```bash
docker compose exec backend python load_data.py
```

---

## 7. Créer les utilisateurs

```bash
docker compose exec backend python create_users.py
```

### Comptes de test

| Rôle            | Username        | Mot de passe |
|-----------------|-----------------|--------------|
| Administrateur  | admin           | admin123     |
| Gestionnaire    | gestionnaire    | gest123      |
| Professionnel   | professionnel   | pro123       |
| Assuré          | assure          | assure123    |

---

## 8. Refaire tout le Feature Engineering + Entraînement

Lancez les commandes **dans cet ordre exact** :

```bash
# 1. Fusion factures + labels + suppression des fuites de données
docker compose exec backend python prepare_data.py

# 2. Feature Engineering v1 (délais, week-end, heure...)
docker compose exec backend python feature_engineering_v1.py

# 3. Feature Engineering v2 (lignes de facture)
docker compose exec backend python feature_engineering_v2.py

# 4. Feature Engineering v3 (tarifs + prestataires)
docker compose exec backend python feature_engineering_v3.py

# 5. Création du dataset final
docker compose exec backend python prepare_final_dataset.py

# 6. Entraînement du modèle XGBoost (le plus long)
docker compose exec backend python train_model.py
```

À la fin de l’entraînement vous devez voir :
- Un rapport de classification
- Recall ≈ 78 %
- Message de sauvegarde du modèle

### Vérifier que le modèle est bien créé

```bash
docker compose exec backend ls -la /ml/models
```

Vous devez voir :
- `fraud_model_xgb.pkl`
- `feature_names.pkl`

---

## 9. Configurer n8n (Alertes)

1. Allez sur http://localhost:5679
2. Créez un compte / connectez-vous
3. Créez un nouveau workflow
4. Ajoutez un nœud **Webhook** :
   - Method : `POST`
   - Path : `fraude-alerte`
5. Ajoutez un nœud **IF** :
   - Condition : `{{ $json.score_fraude }} > 0.8`
6. Sur la branche **true**, ajoutez un nœud de notification (Set, Email, Slack…)
7. **Publiez** le workflow

Vérifiez dans le fichier `backend/app/api/predict.py` que l’URL est bien :

```python
N8N_WEBHOOK_URL = "http://n8n:5678/webhook/fraude-alerte"
```

Puis redémarrez le backend :

```bash
docker compose restart backend
```

---

## 10. Tester le pipeline complet

1. Allez sur http://localhost:8000/docs
2. Ouvrez **POST /predict/**
3. Utilisez un JSON avec des valeurs élevées (surfacturation, week-end, etc.)
4. Vérifiez que la réponse contient :
   - `"score_fraude"`
   - `"explication"` (SHAP)
   - `"alerte_envoyee": true`
5. Vérifiez dans n8n (onglet **Executions**) qu’une exécution est apparue

---

## Commandes utiles

| Action                              | Commande                              |
|-------------------------------------|---------------------------------------|
| Voir les logs du backend            | `docker compose logs backend -f`      |
| Redémarrer le backend               | `docker compose restart backend`      |
| Arrêter la plateforme               | `docker compose down`                 |
| Tout supprimer (y compris les volumes) | `docker compose down -v`           |

---

## Pipeline final obtenu

```
Données brutes
    ↓
Feature Engineering (v1 → v2 → v3)
    ↓
Entraînement XGBoost + SHAP
    ↓
Endpoint /predict
    ↓
Sauvegarde en base
    ↓
Alerte n8n (si score > 0.8)
```

---

## Auteurs

Équipe Capstone – PrediCare TPA
