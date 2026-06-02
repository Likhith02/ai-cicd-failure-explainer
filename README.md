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



The MVP is simple:
Paste a failed CI/CD log -> click Analyze -> get a summary, root cause, error lines, and suggested fix.

