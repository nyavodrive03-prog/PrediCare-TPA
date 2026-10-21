# Compte rendu de test - version B

## Validé
- Authentification via l'API de l'équipe : login, JWT, /auth/me, 4 rôles
- Frontend par rôle (assuré, professionnel, gestionnaire, administrateur)
- Assistant RAG : 369 extraits indexés, outils mes_remboursements et chercher_documents
- Workflow n8n d'alerte fraude : Webhook POST, filtre score > 0,8, testé (réponse 200)
- Dashboard décisionnel : filtres, indicateurs, graphiques, export CSV

## Provisoire
- Factures, assurés et profils : tables de démonstration (*_prov)
- Liste des utilisateurs de l'admin : lit encore utilisateurs_prov

## Limites constatées
- Garde-fou hors sujet insuffisant (l'assistant propose de chercher des recettes)
- Plafond pharmacie erroné dans une réponse (200 000 000 Ar au lieu de 2 000 000 Ar)

## Bloqué côté équipe
- Modèle de fraude absent (fraud_model_xgb.pkl, feature_names.pkl) : /predict/ renvoie 500
- 12 tables réduites à id, 02_schema.sql vide, referentiel_medicaments vide
- /predict/ non protégé par JWT, seuils codés en dur (0,5 et 0,8), features non documentées
