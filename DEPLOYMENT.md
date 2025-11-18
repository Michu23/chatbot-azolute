# Azolute AI Chatbot - Deployment Guide

Complete guide for deploying the Azolute AI Chatbot platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Widget Deployment](#widget-deployment)
7. [Production Checklist](#production-checklist)

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker & Docker Compose (recommended) OR
- Python 3.11+, Node.js 18+, PostgreSQL 14+
- Domain name with DNS access
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd chatbot-azolute
```

2. Create environment files:
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with production values

# Frontend
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with production values
```

3. Update `docker-compose.yml` for production:
```yaml
# Remove volume mounts for hot reload
# Set environment to production
# Configure proper restart policies
```

4. Start services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

### Option 2: Manual Deployment

#### Backend Setup

1. Install Python dependencies:
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb azolute
sudo -u postgres psql -c "CREATE USER azolute WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE azolute TO azolute;"
```

3. Enable pgvector extension:
```bash
sudo -u postgres psql azolute -c "CREATE EXTENSION vector;"
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with production values
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Set up systemd service:
```bash
sudo nano /etc/systemd/system/azolute-backend.service
```

Content:
```ini
[Unit]
Description=Azolute AI Backend
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/azolute/backend
Environment="PATH=/var/www/azolute/backend/venv/bin"
ExecStart=/var/www/azolute/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable azolute-backend
sudo systemctl start azolute-backend
```

#### Frontend Setup

1. Install dependencies and build:
```bash
cd frontend
npm install
npm run build
```

2. Set up systemd service:
```bash
sudo nano /etc/systemd/system/azolute-frontend.service
```

Content:
```ini
[Unit]
Description=Azolute AI Frontend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/azolute/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable azolute-frontend
sudo systemctl start azolute-frontend
```

## Nginx Configuration

1. Install Nginx:
```bash
sudo apt install nginx
```

2. Configure sites:
```bash
sudo nano /etc/nginx/sites-available/azolute
```

Content:
```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Widget
server {
    listen 80;
    server_name widget.yourdomain.com;

    root /var/www/azolute/widget;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        add_header Access-Control-Allow-Origin *;
    }
}
```

3. Enable site and obtain SSL:
```bash
sudo ln -s /etc/nginx/sites-available/azolute /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificates
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com -d widget.yourdomain.com
```

## Database Setup

### Backup Strategy

1. Automated daily backups:
```bash
sudo nano /usr/local/bin/backup-azolute-db.sh
```

Content:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/azolute"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U azolute azolute | gzip > $BACKUP_DIR/azolute_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "azolute_*.sql.gz" -mtime +30 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup-azolute-db.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-azolute-db.sh
```

## Production Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://azolute:STRONG_PASSWORD@localhost:5432/azolute

# Security
SECRET_KEY=generate-with-openssl-rand-base64-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Use production SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Azolute AI

# Frontend URL
FRONTEND_URL=https://app.yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-your-production-key

# Environment
ENVIRONMENT=production

# CORS
CORS_ORIGINS=https://app.yourdomain.com,https://widget.yourdomain.com

# Redis (if using)
REDIS_URL=redis://localhost:6379
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WIDGET_URL=https://widget.yourdomain.com
```

## Monitoring & Logging

### Set up logging

1. Configure log rotation:
```bash
sudo nano /etc/logrotate.d/azolute
```

Content:
```
/var/log/azolute/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Monitor with PM2 (alternative to systemd)

```bash
npm install -g pm2

# Backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name azolute-backend

# Frontend
pm2 start npm --name azolute-frontend -- start

# Save and auto-start
pm2 save
pm2 startup
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Enable firewall (ufw)
- [ ] Configure fail2ban
- [ ] Set up SSL/TLS
- [ ] Enable CORS properly
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Environment variables secured
- [ ] API keys rotated regularly

## Performance Optimization

1. Enable Redis caching
2. Use CDN for static assets
3. Configure PostgreSQL for production
4. Set up monitoring (Sentry, etc.)
5. Implement database connection pooling
6. Enable gzip compression
7. Configure caching headers

## Scaling

### Horizontal Scaling

1. Use load balancer (Nginx, HAProxy)
2. Deploy multiple backend instances
3. Use managed PostgreSQL (AWS RDS, etc.)
4. Use managed Redis cluster
5. Implement queue system (Celery + Redis)

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_chat_sessions_bot_id ON chat_sessions(bot_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX idx_knowledge_sources_bot_id ON knowledge_sources(bot_id);

-- Vector index for similarity search
CREATE INDEX idx_document_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check PostgreSQL is running
   - Verify credentials in .env
   - Check network connectivity

2. **CORS errors**
   - Verify CORS_ORIGINS in backend .env
   - Check Nginx configuration

3. **Widget not loading**
   - Check CORS headers
   - Verify API URL in widget code
   - Check browser console for errors

### Logs

```bash
# Backend logs
journalctl -u azolute-backend -f

# Frontend logs
journalctl -u azolute-frontend -f

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

## Maintenance

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Updates

```bash
# Pull latest code
git pull origin main

# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart azolute-backend

# Frontend
cd frontend
npm install
npm run build
sudo systemctl restart azolute-frontend
```

## Support

For issues or questions:
- GitHub Issues: [repository-url]/issues
- Email: support@azolute.com
- Documentation: https://docs.azolute.com
