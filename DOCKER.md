# Docker Deployment Guide

## Agentic AI Loan Verification System - Docker Setup

This guide explains how to build and run the Loan Verification System using Docker.

---

## 📋 Prerequisites

- Docker 20.10+ installed
- Docker Compose 1.29+ installed
- API Keys:
  - Gemini API Key (from Google AI Studio)
  - Serper API Key (from serper.dev)

---

## 🚀 Quick Start

### 1. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
DATABASE_PATH=./loan_verification.db
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access the Application

- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Commands

### Building

```bash
# Build the Docker image
docker build -t loan-verification:latest .

# Build with specific tag
docker build -t loan-verification:v1.0 .

# Build with no cache
docker build --no-cache -t loan-verification:latest .
```

### Running

```bash
# Run with docker-compose (recommended)
docker-compose up -d

# Run standalone container
docker run -d \
  --name loan-verification \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e SERPER_API_KEY=your_key \
  -v loan-data:/app/data \
  loan-verification:latest

# Run in interactive mode
docker run -it --rm \
  -p 8000:8000 \
  --env-file .env \
  loan-verification:latest
```

### Managing Containers

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart containers
docker-compose restart

# View logs
docker-compose logs -f loan-verification-api

# Execute commands in running container
docker-compose exec loan-verification-api bash

# View container stats
docker stats loan-verification-system
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove images
docker rmi loan-verification:latest

# Prune all unused Docker resources
docker system prune -a
```

---

## 📁 Docker File Structure

```
Loan-verification/
├── Dockerfile              # Main Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Files to exclude from image
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
└── DOCKER.md             # This file
```

---

## 🔧 Docker Configuration Details

### Dockerfile Features

- **Base Image**: Python 3.11-slim (optimized for size)
- **Multi-stage Build**: Efficient layer caching
- **Non-root User**: Security best practice (runs as `appuser`)
- **Health Check**: Automatic container health monitoring
- **Port**: Exposes 8000 for FastAPI

### Docker Compose Features

- **Volume Persistence**: Database stored in Docker volume
- **Network Isolation**: Custom bridge network
- **Auto-restart**: `unless-stopped` policy
- **Environment Variables**: Loaded from `.env` file
- **Development Mode**: Code mounted for hot-reload
- **Health Monitoring**: Built-in health checks

---

## 🔒 Security Considerations

1. **Non-root User**: Container runs as user `appuser` (UID 1000)
2. **Environment Variables**: API keys loaded from `.env` (not committed)
3. **Network Isolation**: Uses custom Docker network
4. **Read-only Filesystem**: Application files owned by appuser
5. **Health Checks**: Automatic container restart on failure

---

## 📊 Volume Management

### Database Persistence

The database is stored in a Docker volume for persistence:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect loan-verification_loan-data

# Backup database
docker run --rm \
  -v loan-verification_loan-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/loan-data-backup.tar.gz -C /data .

# Restore database
docker run --rm \
  -v loan-verification_loan-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/loan-data-backup.tar.gz -C /data
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check container status
docker ps -a

# Inspect container
docker inspect loan-verification-system
```

### Health check failing

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' loan-verification-system

# Test health endpoint manually
docker exec loan-verification-system curl http://localhost:8000/health
```

### Permission issues

```bash
# Fix volume permissions
docker-compose exec loan-verification-api chown -R appuser:appuser /app/data
```

### API keys not working

```bash
# Verify environment variables
docker-compose exec loan-verification-api env | grep API_KEY
```

---

## 🚀 Production Deployment

### Production Dockerfile

For production, create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application (no volumes in production)
COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Production Docker Compose

```yaml
version: '3.8'

services:
  loan-verification-api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
    volumes:
      - loan-data:/app/data
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

volumes:
  loan-data:
```

### Deploy to Production

```bash
# Build production image
docker build -f Dockerfile.prod -t loan-verification:prod .

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d

# Scale horizontally
docker-compose -f docker-compose.prod.yml up -d --scale loan-verification-api=3
```

---

## 📈 Monitoring

### View Container Metrics

```bash
# Real-time stats
docker stats loan-verification-system

# Container logs with timestamps
docker-compose logs -f --timestamps

# Filter logs by service
docker-compose logs -f loan-verification-api
```

### Health Check Status

```bash
# Check health
docker inspect --format='{{.State.Health.Status}}' loan-verification-system

# View health history
docker inspect --format='{{json .State.Health}}' loan-verification-system | jq
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t loan-verification:latest .
      
      - name: Run tests
        run: |
          docker run --rm loan-verification:latest pytest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push loan-verification:latest
```

---

## 🌐 Cloud Deployment

### AWS ECS

```bash
# Tag image for ECR
docker tag loan-verification:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/loan-verification:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/loan-verification:latest
```

### Google Cloud Run

```bash
# Tag for GCR
docker tag loan-verification:latest gcr.io/<project-id>/loan-verification:latest

# Push to GCR
docker push gcr.io/<project-id>/loan-verification:latest
```

### Azure Container Instances

```bash
# Tag for ACR
docker tag loan-verification:latest <registry>.azurecr.io/loan-verification:latest

# Push to ACR
docker push <registry>.azurecr.io/loan-verification:latest
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 🆘 Support

For issues or questions:

1. Check container logs: `docker-compose logs`
2. Verify environment variables: `docker-compose config`
3. Test health endpoint: `curl http://localhost:8000/health`
4. Review main documentation: `README.md`

---

**Built with ❤️ using Docker, FastAPI, and Python**
