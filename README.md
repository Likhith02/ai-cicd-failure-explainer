# AI CI/CD Failure Explainer

A beginner-friendly DevOps + Gen AI project.

The app lets a user paste a failed CI/CD log and returns:

- failure summary
- likely root cause
- important error lines
- suggested fix
- confidence level

## MVP Goal

Paste failed log -> click Analyze -> get an explanation.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- Gen AI: OpenAI API, optional
- DevOps: Docker + GitHub Actions

## Project Structure

```text
ai-cicd-failure-explainer/
  frontend/
  backend/
  docker-compose.yml
  README.md
  .github/
    workflows/
      ci.yml
```

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Optional: Enable Gen AI

Create a `.env` file or set an environment variable:

```bash
set OPENAI_API_KEY=your_api_key_here
```

Without an API key, the backend uses a simple rule-based analyzer so the MVP still works.

## Run With Docker

```bash
docker compose up --build
```

## Weekly LinkedIn Progress Plan

Post 3 times per week:

1. What I learned
2. What I built
3. What was difficult and what I will do next

## First LinkedIn Post

```text
I started building my first DevOps + Gen AI project: AI CI/CD Failure Explainer.

The MVP is simple:
Paste a failed CI/CD log -> click Analyze -> get a summary, root cause, error lines, and suggested fix.

Today I created the project structure with React, FastAPI, Docker, and GitHub Actions.

I will share progress 3 times a week as I build this in public.
```
