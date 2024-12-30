from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext

router = APIRouter(prefix="/profile", tags=["Profile"])
templates = Jinja2Templates(directory="app/templates")

# Şifreleme için Passlib kullanımı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    # Mevcut kullanıcıyı veritabanından çekiyoruz
    admin = db.query(User).first()
    if not admin:
        return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("profile.html", {"request": request, "user": admin})

@router.post("/update-email")
async def update_email(
    new_email: str = Form(...),
    db: Session = Depends(get_db),
):
    # Mevcut kullanıcıyı çekiyoruz
    admin = db.query(User).first()
    if admin:
        admin.email = new_email
        db.commit()
        return RedirectResponse(url="/profile", status_code=303)
    return {"error": "Unable to update email"}

@router.post("/update-password")
async def update_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Mevcut kullanıcıyı çekiyoruz
    admin = db.query(User).first()
    if not admin:
        return RedirectResponse(url="/auth/login")
    
    # Eski şifre doğrulama
    if not pwd_context.verify(current_password, admin.password):
        return templates.TemplateResponse(
            "profile.html",
            {"request": Request, "user": admin, "error": "Current password is incorrect"}
        )

    # Yeni şifre doğrulama
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile.html",
            {"request": Request, "user": admin, "error": "New passwords do not match"}
        )

    # Şifreyi güncelle
    admin.password = pwd_context.hash(new_password)
    db.commit()
    return RedirectResponse(url="/profile", status_code=303)
