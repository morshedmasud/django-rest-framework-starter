# Deployment Guide

**Host Nginx + Docker Backend**

This document describes how to deploy the application on a server that already hosts other websites using **host-level Nginx**, while keeping the backend fully containerized.

> **Key rule:**  
> Only the **host Nginx** listens on ports **80 and 443**.  
> Docker containers run behind it on internal ports and networks.

---

## Architecture Overview

```
Internet
   |
   v
Host Nginx (80 / 443, SSL termination)
   |
   v
Backend Container (Django/API :8000, internal only)
```

---

## Prerequisites

- Linux server with Nginx, Docker, Certbot
- DNS records:
  - api.yourdomain.com

## 1. Install Docker and Create Docker Network

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

docker network create app-network

sudo usermod -aG docker $USER

echo "YOUR_ACCESS_TOKEN" | docker login -u YOUR_USERNAME --password-stdin

```

---

## 2. Create and run redis container

```bash
docker run -d --name redis --network app-network --restart unless-stopped redis:alpine
```

## 3. Run the backend container

Migrations, `collectstatic` and the admin user (from `ADMIN_EMAIL`/`ADMIN_PASSWORD`) are handled by
`entrypoint.sh` on startup. Static files are served by WhiteNoise, so Nginx only needs to proxy.

```bash
docker build -t api .
docker run -d --name api --network app-network --restart unless-stopped \
  --env-file .env.production \
  -e DB_CHOICE=postgres -e DATABASE_URL=postgres://user:password@db-host:5432/dbname \
  -e CELERY_BROKER_URL=redis://redis:6379/0 \
  -v /home/main/media:/app/media \
  -p 127.0.0.1:7080:8000 api

# Celery worker (skips migrations)
docker run -d --name api-worker --network app-network --restart unless-stopped \
  --env-file .env.production -e RUN_MIGRATIONS=0 \
  -e DB_CHOICE=postgres -e DATABASE_URL=postgres://user:password@db-host:5432/dbname \
  -e CELERY_BROKER_URL=redis://redis:6379/0 \
  api celery -A main worker --loglevel=info
```

Production env must have `DEBUG=0`, a strong `SECRET_KEY`, and `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`
set to your domain. Never commit the production env file.

---

## 4. Host Nginx Config – API

Create `/etc/nginx/sites-available/api.yourdomain.com`

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location /media/ {
        alias /home/main/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:7080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 5. SSL Certificates

```bash
sudo certbot --nginx -d api.yourdomain.com
```

---

## 6. Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Summary

- Host Nginx owns ports 80/443
- Backend container is internal only
- Other host sites remain unaffected
