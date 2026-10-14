from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Assures(Base):
    __tablename__ = "assures"
    id = Column(Integer, primary_key=True, index=True)
    # Ajoute les colonnes selon ton CSV plus tard si besoin
    # Pour l’instant on charge tout en texte pour aller vite

class Contrats(Base):
    __tablename__ = "contrats"
    id = Column(Integer, primary_key=True, index=True)

class Factures(Base):
    __tablename__ = "factures"
    id = Column(Integer, primary_key=True, index=True)

class Garanties(Base):
    __tablename__ = "garanties"
    id = Column(Integer, primary_key=True, index=True)

class GrilleTarifaire(Base):
    __tablename__ = "grille_tarifaire"
    id = Column(Integer, primary_key=True, index=True)

class IdentitesPii(Base):
    __tablename__ = "identites_pii"
    id = Column(Integer, primary_key=True, index=True)

class LignesFacture(Base):
    __tablename__ = "lignes_facture"
    id = Column(Integer, primary_key=True, index=True)

class Ordonnances(Base):
    __tablename__ = "ordonnances"
    id = Column(Integer, primary_key=True, index=True)

class OrdonnancesLignes(Base):
    __tablename__ = "ordonnances_lignes"
    id = Column(Integer, primary_key=True, index=True)

class Prestataires(Base):
    __tablename__ = "prestataires"
    id = Column(Integer, primary_key=True, index=True)

class ReferentielActes(Base):
    __tablename__ = "referentiel_actes"
    id = Column(Integer, primary_key=True, index=True)

class ReferentielMedicaments(Base):
    __tablename__ = "referentiel_medicaments"
    id = Column(Integer, primary_key=True, index=True)

# Table des utilisateurs (pour l’authentification)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, gestionnaire, professionnel, assure
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(String, nullable=True)
    score_fraude = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    explication = Column(Text, nullable=True)  # On stockera le JSON en texte
    created_at = Column(DateTime(timezone=True), server_default=func.now())