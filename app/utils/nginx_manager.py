import subprocess

def create_nginx_config(domain, subdomain=None, root_path=None):
    try:
        if subdomain:
            server_name = f"{subdomain}.{domain}"
        else:
            server_name = domain

        config_path = f"/etc/nginx/sites-available/{server_name}"
        with open(config_path, "w") as f:
            f.write(f"""
server {{
    listen 80;
    server_name {server_name};

    root {root_path};
    index index.html;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
""")
        # Symbolic link oluştur
        subprocess.run(["sudo", "ln", "-sf", config_path, f"/etc/nginx/sites-enabled/{server_name}"], check=True)
        # Nginx'i yeniden yükle
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        return f"Nginx configuration for {server_name} created successfully."
    except Exception as e:
        return f"Error creating Nginx config: {str(e)}"

def delete_nginx_config(domain, subdomain=None):
    try:
        if subdomain:
            server_name = f"{subdomain}.{domain}"
        else:
            server_name = domain

        config_path = f"/etc/nginx/sites-available/{server_name}"
        symlink_path = f"/etc/nginx/sites-enabled/{server_name}"
        
        # Konfigürasyon dosyasını ve symlink'i sil
        subprocess.run(["sudo", "rm", "-f", config_path, symlink_path], check=True)
        # Nginx'i yeniden yükle
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        return f"Nginx configuration for {server_name} deleted successfully."
    except Exception as e:
        return f"Error deleting Nginx config: {str(e)}"
