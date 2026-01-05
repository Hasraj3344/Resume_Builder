# 🐳 Docker Deployment - Quick Start

Deploy your Resume Builder in **under 5 minutes** using Docker!

## ⚡ Super Quick Start

```bash
# 1. Copy environment template
cp .env.production .env

# 2. Edit with your API keys (required)
nano .env

# 3. Deploy!
./deploy.sh start
```

That's it! Access at **http://localhost**

---

## 📋 What You Need

### Required:
- **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- **JWT Secret** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### Optional (for payments):
- **PayPal Client ID & Secret** - From https://developer.paypal.com/

---

## 🔧 Quick Configuration

Edit `.env` file:

```bash
# REQUIRED - Add your OpenAI key
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# REQUIRED - Generate a random secret
JWT_SECRET_KEY=YOUR_RANDOM_SECRET_HERE

# OPTIONAL - For live payments (use sandbox for testing)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_secret
```

---

## 🚀 Deployment Commands

```bash
# Start the application
./deploy.sh start

# Stop the application
./deploy.sh stop

# Restart after changes
./deploy.sh restart

# View live logs
./deploy.sh logs

# Update to latest version
./deploy.sh update

# Backup database
./deploy.sh backup

# Check status
./deploy.sh status
```

---

## 🌐 Access Points

After deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost | Main frontend |
| **API** | http://localhost:8000 | Backend API |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Health Check** | http://localhost:8000/health | Backend health |

---

## 🔍 Troubleshooting

### Port already in use?

```bash
# Change ports in docker-compose.yml
ports:
  - "8080:80"    # Frontend on port 8080
  - "8001:8000"  # Backend on port 8001
```

### Container won't start?

```bash
# Check logs
./deploy.sh logs

# Or check specific service
docker-compose logs backend
docker-compose logs frontend
```

### Database errors?

```bash
# Restart backend
docker-compose restart backend

# Or recreate database
rm data/resume_builder.db
docker-compose restart backend
```

### "Permission denied" error?

```bash
# Make script executable
chmod +x deploy.sh

# Or run directly
bash deploy.sh start
```

---

## 🌍 Deploy to Production (VPS)

### 1. Get a VPS

Recommended providers:
- **Hetzner** - €3.79/month (best value)
- **DigitalOcean** - $6/month
- **Linode** - $5/month

### 2. Connect to VPS

```bash
ssh root@your-vps-ip
```

### 3. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 4. Clone and Deploy

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/Resume_Builder.git
cd Resume_Builder

# Configure
cp .env.production .env
nano .env  # Add your keys

# Deploy
./deploy.sh start
```

### 5. Set up Domain (Optional)

```bash
# Install Nginx (for reverse proxy)
apt install nginx -y

# Configure Nginx
nano /etc/nginx/sites-available/default
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Restart Nginx:

```bash
nginx -t
systemctl restart nginx
```

### 6. Add SSL (Free with Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 📊 Monitoring

### View logs in real-time

```bash
./deploy.sh logs
```

### Check resource usage

```bash
docker stats
```

### Check disk space

```bash
df -h
```

---

## 💾 Backup & Restore

### Automatic Backup

```bash
# Create backup
./deploy.sh backup

# Backups saved to: ./backups/backup-YYYYMMDD-HHMMSS.db
```

### Manual Backup

```bash
# Backup database
docker cp resume-builder-backend:/data/resume_builder.db ./backup.db

# Backup uploaded files
docker cp resume-builder-backend:/app/uploads ./uploads-backup
```

### Restore Backup

```bash
# Stop services
./deploy.sh stop

# Restore database
cp backup.db data/resume_builder.db

# Restore uploads
cp -r uploads-backup/* uploads/

# Start services
./deploy.sh start
```

---

## 🔄 Updating

```bash
# Pull latest changes
git pull origin main

# Update and rebuild
./deploy.sh update
```

---

## 📞 Need Help?

- **Documentation**: See `DOCKER_DEPLOYMENT.md` for detailed guide
- **Issues**: https://github.com/YOUR_USERNAME/Resume_Builder/issues
- **Logs**: `./deploy.sh logs`

---

## ✅ Success Checklist

- [ ] Docker installed
- [ ] `.env` file configured with API keys
- [ ] Application started: `./deploy.sh start`
- [ ] Frontend accessible at http://localhost
- [ ] Backend healthy at http://localhost:8000/health
- [ ] Can create account and upload resume
- [ ] Can generate optimized resume

**You're ready to go!** 🎉
