import sys
import os

# Proje kök dizinini Python yoluna ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Yeni şifre
new_password = "admin"

# Veritabanı bağlantısı
db = SessionLocal()

# Admin kullanıcısını bul ve şifreyi değiştir
admin = db.query(User).filter(User.email == "admin@example.com").first()
if admin:
    admin.password = pwd_context.hash(new_password)
    db.commit()
    print("Password successfully updated!")
else:
    print("Admin user not found!")

db.close()
