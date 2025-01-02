from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Domain, Subdomain
from app.utils.nginx_manager import create_nginx_config, delete_nginx_config
from app.utils.dns_manager import configure_zone, restart_bind9

router = APIRouter(prefix="/domain", tags=["Domain Management"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def domain_page(request: Request):  # Burada `Request` türü belirtildi
    return templates.TemplateResponse("domain.html", {"request": request})

@router.post("/add-domain")
async def add_domain(domain_name: str = Form(...), ip_address: str = "192.168.1.100", db: Session = Depends(get_db)):
    root_path = f"/var/www/{domain_name}"
    new_domain = Domain(domain_name=domain_name, root_path=root_path)
    db.add(new_domain)
    db.commit()

    # Bind9 zone dosyasını oluştur
    dns_result = configure_zone(domain_name, ip_address)

    # Nginx konfigürasyonu oluştur
    nginx_result = create_nginx_config(domain_name, root_path=root_path)

    # Bind9'u yeniden başlat
    restart_result = restart_bind9()

    return {
        "dns_result": dns_result,
        "nginx_result": nginx_result,
        "restart_result": restart_result,
    }

@router.post("/add-subdomain")
async def add_subdomain(domain_name: str = Form(...), subdomain_name: str = Form(...), ip_address: str = "192.168.1.100", db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.domain_name == domain_name).first()
    if not domain:
        return {"message": "Parent domain not found."}

    root_path = f"/var/www/{subdomain_name}.{domain_name}"
    new_subdomain = Subdomain(subdomain_name=subdomain_name, root_path=root_path, domain_id=domain.id)
    db.add(new_subdomain)
    db.commit()

    # Bind9 zone dosyasını oluştur (subdomain)
    full_domain_name = f"{subdomain_name}.{domain_name}"
    dns_result = configure_zone(full_domain_name, ip_address)

    # Nginx konfigürasyonu oluştur (subdomain)
    nginx_result = create_nginx_config(full_domain_name, root_path=root_path)

    # Bind9'u yeniden başlat
    restart_result = restart_bind9()

    return {
        "dns_result": dns_result,
        "nginx_result": nginx_result,
        "restart_result": restart_result,
    }
