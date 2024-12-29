### Deploy
```bash
cp .env.example .env
cp .config.example.yaml .config.yaml
docker compose up -d --build
docker exec -it support bash
alembic upgrade head
python -m bot
```
