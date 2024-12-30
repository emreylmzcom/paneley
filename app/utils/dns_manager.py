import subprocess
from sqlalchemy.orm import Session
from app.models import DNSRecord

def install_bind9():
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "bind9"], check=True)
        return "Bind9 DNS server successfully installed."
    except subprocess.CalledProcessError as e:
        return f"Error during Bind9 installation: {str(e)}"

def restart_bind9():
    try:
        subprocess.run(["sudo", "systemctl", "restart", "bind9"], check=True)
        return "Bind9 DNS server restarted successfully."
    except subprocess.CalledProcessError as e:
        return f"Error during Bind9 restart: {str(e)}"

def configure_zone(domain_name, ip_address):
    try:
        zone_file = f"/etc/bind/zones/{domain_name}.db"
        with open(zone_file, "w") as f:
            f.write(f"""
$TTL    604800
@       IN      SOA     ns1.{domain_name}. admin.{domain_name}. (
                        2         ; Serial
                        604800    ; Refresh
                        86400     ; Retry
                        2419200   ; Expire
                        604800 )  ; Negative Cache TTL
;
@       IN      NS      ns1.{domain_name}.
@       IN      A       {ip_address}
www     IN      A       {ip_address}
""")
        subprocess.run(["sudo", "systemctl", "reload", "bind9"], check=True)
        return f"Zone file for {domain_name} successfully created and reloaded."
    except Exception as e:
        return f"Error configuring zone: {str(e)}"

def configure_zone_from_db(db: Session):
    try:
        # Tüm DNS kayıtlarını getir
        dns_records = db.query(DNSRecord).all()

        # Zone dosyasını oluştur
        zone_file_path = "/etc/bind/zones/db.local"
        with open(zone_file_path, "w") as f:
            f.write(f"$TTL    604800\n")
            f.write(f"@       IN      SOA     ns1.local. admin.local. (\n")
            f.write(f"                        2         ; Serial\n")
            f.write(f"                        604800    ; Refresh\n")
            f.write(f"                        86400     ; Retry\n")
            f.write(f"                        2419200   ; Expire\n")
            f.write(f"                        604800 )  ; Negative Cache TTL\n")
            f.write(f";\n")
            
            for record in dns_records:
                f.write(f"{record.domain}    IN      A       {record.ip_address}\n")

        subprocess.run(["sudo", "systemctl", "reload", "bind9"], check=True)
        return "Zone file successfully updated and Bind9 reloaded."

    except Exception as e:
        return f"Error configuring zone: {str(e)}"
