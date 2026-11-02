# Docker Desktop — Quick Test Guide

Pull and run both images locally to verify they're working.

## Prerequisites
- Docker Desktop running on your machine

---

## Backend

```bash
docker pull <your-dockerhub-username>/hirewise-backend:latest

docker run -d \
  --name hirewise-backend \
  -p 8000:8000 \
  -e GROQ_API_KEY=<your-key> \
  -e JWT_SECRET_KEY=<your-secret> \
  <your-dockerhub-username>/hirewise-backend:latest
```

Health check → open http://localhost:8000/health in your browser.

---

## Frontend

```bash
docker pull <your-dockerhub-username>/hirewise-frontend:latest

docker run -d \
  --name hirewise-frontend \
  -p 3000:80 \
  <your-dockerhub-username>/hirewise-frontend:latest
```

Open http://localhost:3000 in your browser.

---

## GitHub Secrets to add

Go to **GitHub → Your Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name       | Value                        |
|-------------------|------------------------------|
| `DOCKER_USERNAME` | Your Docker Hub username     |
| `DOCKER_PASSWORD` | Your Docker Hub password     |
