# OpenAlgo Coolify Deployment Guide

This guide explains how to deploy OpenAlgo on Coolify, a self-hosted platform for deploying applications.

## Prerequisites

1. A Coolify instance running on your server
2. Access to the Coolify web interface
3. Basic knowledge of Docker and environment variables

## Deployment Steps

### 1. Create New Application in Coolify

1. Log into your Coolify instance
2. Click "Add New Resource"
3. Select "Docker Compose"
4. Choose your deployment source (Git repository or Docker image)

### 2. Configure Docker Compose

Use the provided `docker-compose.yaml` file in this repository. The file has been optimized for Coolify with:

- Named volumes for persistent storage
- Health checks for monitoring
- Proper port exposure
- Coolify-specific labels and network configuration

### 3. Required Environment Variables

Configure the following environment variables in Coolify:

#### Core Application Settings

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_PORT=5000
WEBSOCKET_PORT=8765

# Security (REQUIRED)
SECRET_KEY=your-secret-key-minimum-32-characters-long
API_KEY=your-api-key-for-openalgo-access

# Database Configuration
DATABASE_URL=sqlite:///app/db/openalgo.db

# Logging
LOG_LEVEL=INFO
```

#### Optional Broker Configuration

```bash
# Broker Integration (Optional - configure as needed)
BROKER_NAME=your-broker-name
BROKER_API_KEY=your-broker-api-key
BROKER_API_SECRET=your-broker-api-secret
```

#### WebSocket Configuration

```bash
# WebSocket CORS Settings
WEBSOCKET_CORS_ALLOWED_ORIGINS=*
```

#### Session and Security Settings

```bash
# Session Configuration
SESSION_COOKIE_NAME=openalgo_session
CSRF_COOKIE_NAME=openalgo_csrf
CSRF_ENABLED=TRUE
CSRF_TIME_LIMIT=3600

# Host Configuration (set to your Coolify domain)
HOST_SERVER=https://your-coolify-domain.com
```

#### Optional Advanced Settings

```bash
# CORS Configuration
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=100 per minute

# Ngrok (Development only)
NGROK_ALLOW=FALSE
```

### 4. Environment Variable Generation

For security-critical variables, generate strong values:

```bash
# Generate a strong SECRET_KEY (32+ characters)
SECRET_KEY=$(openssl rand -base64 32)

# Generate a unique API_KEY
API_KEY=$(openssl rand -hex 16)
```

### 5. Volume Configuration

Coolify automatically handles the following persistent volumes:

- `openalgo_db`: Database storage (`/app/db`)
- `openalgo_logs`: Application logs (`/app/logs`)

### 6. Port Configuration

Coolify will automatically map the exposed ports:

- **5000**: Main Flask application
- **8765**: WebSocket server

### 7. Health Monitoring

The application includes a health check endpoint at `/health` that Coolify uses for monitoring:

- **Endpoint**: `http://localhost:5000/health`
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts
- **Start Period**: 40 seconds

### 8. Deployment Process

1. **Configure Environment Variables**: Set all required environment variables in Coolify
2. **Deploy**: Click the deploy button in Coolify
3. **Monitor**: Watch the deployment logs in Coolify
4. **Access**: Once deployed, access your application through the Coolify-provided URL

### 9. Post-Deployment Setup

1. **Initial Setup**: Access your OpenAlgo instance and complete the initial setup
2. **Admin Account**: Create your first admin account
3. **Broker Configuration**: Configure your trading broker(s) through the web interface
4. **API Keys**: Generate additional API keys as needed through the dashboard

## Troubleshooting

### Common Issues

1. **Health Check Failing**
   - Check if the `/health` endpoint is accessible
   - Verify database connectivity
   - Review application logs in Coolify

2. **Database Issues**
   - Ensure the `openalgo_db` volume is properly mounted
   - Check SQLite database permissions
   - Verify DATABASE_URL configuration

3. **WebSocket Connection Issues**
   - Confirm WEBSOCKET_PORT (8765) is properly exposed
   - Check CORS configuration
   - Verify WebSocket proxy is running

4. **CSRF Token Issues**
   - Ensure CSRF_ENABLED is set correctly
   - Check HOST_SERVER matches your domain
   - Verify cookie security settings

### Log Analysis

Monitor these log sources in Coolify:

1. **Application Logs**: Main Flask application logs
2. **Container Logs**: Docker container startup and runtime logs
3. **Health Check Logs**: Health endpoint response logs

### Performance Tuning

For production deployments:

1. **Resource Allocation**: Allocate sufficient CPU and memory based on usage
2. **Database Optimization**: Consider using PostgreSQL for higher loads
3. **Caching**: Implement Redis for session storage and caching
4. **Load Balancing**: Use Coolify's load balancing for multiple instances

## Security Considerations

1. **Environment Variables**: Never commit sensitive environment variables to version control
2. **HTTPS**: Always use HTTPS in production (configure through Coolify)
3. **Firewall**: Ensure proper firewall configuration on your Coolify server
4. **Backup**: Regularly backup your database and configuration
5. **Updates**: Keep Coolify and OpenAlgo updated to the latest versions

## Support

If you encounter issues:

1. Check the OpenAlgo documentation
2. Review Coolify logs and documentation
3. Join the OpenAlgo community for support
4. Submit issues to the OpenAlgo GitHub repository

## Additional Resources

- [Coolify Documentation](https://coolify.io/docs)
- [OpenAlgo Documentation](https://docs.openalgo.in)
- [Docker Compose Reference](https://docs.docker.com/compose/) 