# OpenAlgo - Coolify Deployment

Quick guide for deploying OpenAlgo on Coolify.

## 🚀 Quick Start

1. **Create Application in Coolify**
   - Add New Resource → Docker Compose
   - Use the `docker-compose.yaml` from this repository

2. **Set Required Environment Variables**
   ```bash
   SECRET_KEY=your-32-char-secret-key
   API_KEY=your-unique-api-key
   HOST_SERVER=https://your-domain.com
   ```

3. **Deploy**
   - Click Deploy in Coolify
   - Monitor deployment logs
   - Access via Coolify-provided URL

## 📋 Environment Variables

**Required:**
- `SECRET_KEY` - Generate with `openssl rand -base64 32`
- `API_KEY` - Generate with `openssl rand -hex 16`
- `HOST_SERVER` - Your Coolify domain with https://

**Optional:**
- `BROKER_NAME`, `BROKER_API_KEY`, `BROKER_API_SECRET` - Broker configuration
- `FLASK_ENV=production` - Environment mode
- `FLASK_PORT=5050` - Application port (default: 5050)
- `LOG_LEVEL=INFO` - Logging level

## 🔧 Features

✅ **Automatic Health Monitoring** - `/health` endpoint  
✅ **Persistent Storage** - Database and logs preserved  
✅ **WebSocket Support** - Real-time data streaming  
✅ **Security Optimized** - CSRF protection, secure cookies  
✅ **Production Ready** - Gunicorn with eventlet workers  

## 📖 Detailed Guide

For complete deployment instructions, troubleshooting, and configuration options, see:

**[📚 COOLIFY_DEPLOYMENT.md](./COOLIFY_DEPLOYMENT.md)**

## 🆘 Quick Troubleshooting

- **Health check failing?** Check `/health` endpoint accessibility
- **Database issues?** Verify volume mounting and permissions
- **CSRF errors?** Ensure `HOST_SERVER` matches your domain
- **WebSocket issues?** Check port 8765 exposure and CORS settings
- **Port issues?** Ensure FLASK_PORT matches exposed port (default: 5050)

## 📊 Health Check

Monitor your deployment at: `https://your-domain.com/health`

Returns JSON with status, version, database connectivity, and system info.

---

**Need help?** Check the [detailed deployment guide](./COOLIFY_DEPLOYMENT.md) or join our community! 