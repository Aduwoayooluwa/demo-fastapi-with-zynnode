# launchpad-api

A small Python 3.11 / FastAPI REST API for live deployment demos. No database,
authentication, secrets, Dockerfile, or deployment configuration is needed.

## Run locally

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Starts with no environment variables set. Open http://localhost:8000/docs for
interactive API documentation, or check http://localhost:8000/health.

## Endpoints

| Method | Path | Result |
| --- | --- | --- |
| GET | `/health` | Status, version `1.0.0`, and environment |
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create a task; returns `201` |
| PATCH | `/api/tasks/{id}/toggle` | Flip `done` and return the task |
| DELETE | `/api/tasks/{id}` | Delete a task; returns `204` with no body |
| GET | `/api/stats` | Counts: `total`, `done`, `remaining` |
| GET | `/docs` | Interactive Swagger UI |

Create a task:

```sh
curl -X POST http://localhost:8000/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Try the API"}'
```

Tasks contain `id` (integer), `title` (string), `done` (boolean), and `created_at`
(UTC ISO 8601 string). New tasks start with `done: false`. Titles must contain
1–80 characters. Invalid input returns `422`; missing task IDs return `404`.

Every startup seeds four unfinished tasks: "Write the code", "Push to GitHub",
"Deploy with Zynnode", and "Celebrate". All data lives in memory and resets on
restart. Use a single worker so requests share the same task store.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8000` | HTTP port, read by the shell in the start command |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins; surrounding spaces are trimmed |
| `ENVIRONMENT` | `local` | Environment label returned by `/health` |

All variables are optional. To use `.env.example` locally with the start command:

```sh
cp .env.example .env
set -a
source .env
set +a
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The app does not automatically load `.env`; export variables in your shell or set
them in your deployment platform. For multiple CORS origins in a sourced `.env`,
quote the value, for example `ALLOWED_ORIGINS="http://localhost:3000, https://example.com"`.
