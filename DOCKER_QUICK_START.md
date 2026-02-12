# 🐳 Docker Quick Reference

## Quick Start Commands

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## Access Points

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Container Management

```bash
# Check status
docker-compose ps

# View real-time logs
docker-compose logs -f loan-verification-api

# Execute commands inside container
docker-compose exec loan-verification-api bash

# Restart container
docker-compose restart

# Stop and remove everything
docker-compose down -v
```

## Common Docker Commands

```bash
# List running containers
docker ps

# List all images
docker images

# Check container logs
docker logs loan-verification-system

# Monitor resource usage
docker stats loan-verification-system

# Inspect container
docker inspect loan-verification-system
```

## Environment Setup

Make sure your `.env` file contains:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
docker-compose ps
```

### Check health status
```bash
docker inspect --format='{{.State.Health.Status}}' loan-verification-system
curl http://localhost:8000/health
```

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

For detailed documentation, see `DOCKER.md`
