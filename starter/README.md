# tasks-api — starter kolokwium

REST API w Pythonie (Flask + gunicorn), persystencja w SQLite. Pełna komunikacja z hostem odbywa się przez reverse proxy **nginx**.

## Endpointy aplikacji

| Method | Path     | Opis |
|---|---|---|
| GET    | `/health` | sprawdzenie żywotności (`{"status":"ok"}`) |
| GET    | `/tasks`  | lista zadań |
| POST   | `/tasks`  | tworzy zadanie; body: `{"title":"...", "priority":"low|normal|high"}` |

Aplikacja słucha wewnątrz kontenera na **porcie 8000**. Reverse proxy nginx słucha na **porcie 80** (wewnątrz kontenera) — to nginx ma być wystawiony na host.

## Konfiguracja przez zmienne środowiskowe

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `DB_PATH` | `/data/app.db` | Ścieżka do pliku SQLite (powinien wskazywać na wolumen). |

Aplikacja sama tworzy tabelę `tasks` przy starcie (`CREATE TABLE IF NOT EXISTS`).

## Skrypty (zdefiniowane w środowisku Pythona)

```bash
pip install -r requirements-dev.txt
python -m pytest app/tests -v           # testy
bash scripts/lint.sh                    # lint
gunicorn -b 0.0.0.0:8000 app.main:app   # start serwera (po zainstalowaniu deps)
```

## Pliki dostarczone

```
starter/
├── app/
│   ├── __init__.py
│   ├── main.py            ← Flask app, endpointy
│   ├── db.py              ← SQLite (init_schema, insert, list)
│   ├── validate.py        ← walidacja inputu (czysta logika)
│   └── tests/
│       └── test_validate.py
├── nginx/
│   └── nginx.conf         ← szkielet z TODO — do uzupełnienia
├── scripts/
│   └── lint.sh
├── requirements.txt       ← prod: flask, gunicorn
├── requirements-dev.txt   ← + pytest
├── .gitignore
└── .dockerignore
```

## Co masz zrobić (4 pliki — patrz: treść kolokwium)

1. `Dockerfile` dla aplikacji Python.
2. Uzupełnić `nginx/nginx.conf` (upstream + location z `proxy_pass`).
3. `docker-compose.yml` z dwoma serwisami: `app` + `nginx`.
4. `.github/workflows/ci.yml` (lint → test → build), bez Dockera.

## Smoke test (po napisaniu Dockerfile, compose, nginx.conf)

```bash
docker compose up -d --build
sleep 5
curl http://localhost:8080/health
# {"status":"ok"}
curl -X POST -H 'Content-Type: application/json' \
     -d '{"title":"buy milk","priority":"high"}' \
     http://localhost:8080/tasks
# {"id":1,"title":"buy milk","priority":"high"}
curl http://localhost:8080/tasks
docker compose down
```
