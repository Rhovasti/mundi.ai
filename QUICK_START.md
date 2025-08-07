# Quick Start Commands

Since Docker requires sudo permissions, run these commands manually:

## 1. Build and start all services:

```bash
sudo docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## 2. Monitor the startup:

```bash
# Watch logs for all services
sudo docker compose logs -f

# Or just the main app
sudo docker compose logs -f app
```

## 3. Check service status:

```bash
sudo docker compose ps
```

## 4. Access the application:

Once all services are running:
- **Mundi.ai**: http://localhost:8000
- **MinIO Console**: http://localhost:9001 (admin/password)

## Troubleshooting:

If DriftDB fails to build, you can skip it temporarily by commenting it out in docker-compose.yml:
```yaml
# Comment out in docker-compose.yml:
#  driftdb:
#    ...

# And in app service's depends_on:
depends_on:
  # driftdb:
  #   condition: service_healthy
```

## To stop everything:

```bash
sudo docker compose down
```

## To remove all data and start fresh:

```bash
sudo docker compose down -v
sudo rm -rf data/
```