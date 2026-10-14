from app.db.database import SessionLocal, engine, Base
from app.db.models import User
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

users = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "gestionnaire", "password": "gest123", "role": "gestionnaire"},
    {"username": "professionnel", "password": "pro123", "role": "professionnel"},
    {"username": "assure", "password": "assure123", "role": "assure"},
]

for u in users:
    existing = db.query(User).filter(User.username == u["username"]).first()
    if not existing:
        user = User(
            username=u["username"],
            hashed_password=get_password_hash(u["password"]),
            role=u["role"]
        )
        db.add(user)
        print(f"Utilisateur créé : {u['username']} ({u['role']})")
    else:
        print(f"Utilisateur déjà existant : {u['username']}")

db.commit()
db.close()
print("\nTerminé !")