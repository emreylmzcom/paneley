import platform
import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import auth, profile, dns, domain
import time


app = FastAPI()

# Dashboard için template tanımları
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Login kontrol fonksiyonu
def is_authenticated(request: Request):
    if not request.cookies.get("logged_in"):
        return False
    return True

# Middleware benzeri bir koruma fonksiyonu
def login_required(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login", status_code=303)

# Ana rota yönlendirme
@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.cookies.get("logged_in"):
        return RedirectResponse(url="/auth/login")

    # Sistem bilgilerini çekiyoruz
    os_info = {
        "os_name": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_usage": psutil.cpu_percent(interval=1),  # CPU kullanımı
        "ram_usage": psutil.virtual_memory().percent,  # RAM kullanımı
        "disk_usage": psutil.disk_usage("/").percent,  # Disk kullanımı yüzdesi
        "disk_total": round(psutil.disk_usage("/").total / (1024 ** 3), 2),  # Diskin toplam boyutu (GB)
        "disk_used": round(psutil.disk_usage("/").used / (1024 ** 3), 2),  # Kullanılan disk boyutu (GB)
        "release": platform.release(),
        "disk_free": round(psutil.disk_usage("/").free / (1024 ** 3), 2),  # Boş disk alanı (GB)

    }

    return templates.TemplateResponse("dashboard.html", {"request": request, **os_info})


# Router'ları bağla
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(dns.router)
app.include_router(domain.router)
