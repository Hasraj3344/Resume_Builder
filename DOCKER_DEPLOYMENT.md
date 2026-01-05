# Docker Deployment Guide

This guide covers deploying the Resume Builder application using Docker.

## 📋 Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- Domain name (optional, but recommended for production)
- SSL certificate (optional, for HTTPS)

## 🚀 Quick Start (Local Testing)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Resume_Builder.git
   cd Resume_Builder
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.production .env
   # Edit .env and fill in your API keys
   nano .env
   ```

3. **Build and run**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Production Deployment

### Option 1: Deploy on a VPS (DigitalOcean, Linode, Hetzner, etc.)

#### Step 1: Set up the VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create application directory
mkdir -p /opt/resume-builder
cd /opt/resume-builder
```

#### Step 2: Clone and configure

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Resume_Builder.git .

# Set up environment
cp .env.production .env
nano .env  # Add your keys
```

#### Step 3: Update CORS in .env

```bash
# In .env file, update:
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### Step 4: Deploy

```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Deploy with SSL (Production-Ready)

#### Step 1: Set up domain DNS

Point your domain's A record to your VPS IP:
```
Type: A
Name: @
Value: YOUR_VPS_IP
```

#### Step 2: Install Certbot for SSL

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Stop containers temporarily
cd /opt/resume-builder
docker-compose down

# Get SSL certificate
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

#### Step 3: Update nginx.conf for SSL

Create `nginx-ssl.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    root /usr/share/nginx/html;
    index index.html;

    # Rest of configuration (copy from nginx.conf)
    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        # ... proxy settings ...
    }
}
```

#### Step 4: Update docker-compose.yml

```yaml
frontend:
  # ... other settings ...
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
    - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf
```

#### Step 5: Start with SSL

```bash
docker-compose up -d --build
```

## 🔍 Monitoring and Maintenance

### View logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Check health

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health

# Check containers
docker-compose ps
```

### Restart services

```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend
```

### Update application

```bash
cd /opt/resume-builder

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 💾 Database Management

### Backup SQLite database

```bash
# Create backup
docker-compose exec backend sqlite3 /data/resume_builder.db ".backup /data/backup.db"

# Copy backup to host
docker cp resume-builder-backend:/data/backup.db ./backup-$(date +%Y%m%d).db
```

### Restore database

```bash
# Copy backup to container
docker cp backup-20231215.db resume-builder-backend:/data/restore.db

# Restore
docker-compose exec backend sqlite3 /data/resume_builder.db ".restore /data/restore.db"
```

### Migrate to PostgreSQL (Recommended for Production)

1. **Set up PostgreSQL**:
   ```yaml
   # Add to docker-compose.yml
   postgres:
     image: postgres:15-alpine
     environment:
       - POSTGRES_DB=resume_builder
       - POSTGRES_USER=resume_user
       - POSTGRES_PASSWORD=secure_password
     volumes:
       - postgres_data:/var/lib/postgresql/data
   ```

2. **Update DATABASE_URL**:
   ```bash
   DATABASE_URL=postgresql://resume_user:secure_password@postgres:5432/resume_builder
   ```

3. **Migrate data** (use migration script or manual export/import)

## 🔒 Security Best Practices

1. **Change default secrets**:
   ```bash
   # Generate new JWT secret
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Limit CORS origins**:
   ```bash
   # In .env, only allow your domain
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Enable firewall**:
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp
   ufw enable
   ```

4. **Regular updates**:
   ```bash
   # Weekly maintenance
   docker-compose pull
   docker-compose up -d --build
   apt update && apt upgrade -y
   ```

## 📊 Resource Requirements

### Minimum (1-100 users):
- CPU: 1 vCPU
- RAM: 1GB
- Storage: 10GB SSD

### Recommended (100-1000 users):
- CPU: 2 vCPU
- RAM: 4GB
- Storage: 50GB SSD

### Scaling (1000+ users):
- Consider Kubernetes or container orchestration
- Use PostgreSQL instead of SQLite
- Add Redis for caching
- Use S3 for file storage

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check resources
docker stats
```

### Database locked error

```bash
# Restart backend
docker-compose restart backend
```

### Out of memory

```bash
# Check memory usage
docker stats

# Add swap space
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Permission errors

```bash
# Fix permissions
chown -R 1000:1000 data/ output/ uploads/
```

## 📞 Support

- GitHub Issues: https://github.com/YOUR_USERNAME/Resume_Builder/issues
- Documentation: See CLAUDE.md for architecture details

## 🎉 Success!

Your Resume Builder is now deployed! Access it at:
- https://yourdomain.com

Monitor it with:
```bash
docker-compose ps
docker-compose logs -f
```
