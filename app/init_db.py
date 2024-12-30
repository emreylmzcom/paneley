import sys
import os

# Proje kök dizinini Python yoluna ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine
from app.models import Base

def init_db():
    """
    Veritabanındaki tüm tabloları oluşturur.
    """
    print("Tablolar oluşturuluyor...")
    Base.metadata.create_all(bind=engine)
    print("Tablolar başarıyla oluşturuldu.")

if __name__ == "__main__":
    init_db()
