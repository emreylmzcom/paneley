from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.utils.dns_manager import install_bind9, restart_bind9, configure_zone, configure_zone_from_db
from app.models import DNSRecord

router = APIRouter(prefix="/dns", tags=["DNS"])  # Burada "prefix" ve "tags" güncellendi
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def dns_management_page(request: Request, db: Session = Depends(get_db)):
    dns_records = db.query(DNSRecord).all()
    return templates.TemplateResponse("dns_management.html", {"request": request, "dns_records": dns_records})

@router.post("/install")
async def install_dns():
    result = install_bind9()
    return {"message": result}

@router.post("/restart")
async def restart_dns():
    result = restart_bind9()
    return {"message": result}

@router.post("/add-domain")
async def add_domain(domain_name: str = Form(...), ip_address: str = Form(...), db: Session = Depends(get_db)):
    record = DNSRecord(domain=domain_name, ip_address=ip_address)
    db.add(record)
    db.commit()
    configure_zone_from_db(db)
    return {"message": f"Domain {domain_name} added and zone updated."}

@router.get("/update-zones")
async def update_zones(db: Session = Depends(get_db)):
    result = configure_zone_from_db(db)
    return {"message": result}
