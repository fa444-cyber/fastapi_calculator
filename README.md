# FastAPI Calculator

A FastAPI calculator web app with add, subtract, multiply, and divide operations, request logging, a browser interface, and user accounts stored in PostgreSQL with hashed passwords.

## Docker Hub

Image: https://hub.docker.com/r/fayada/fastapi_calculator

Pull and run it:

```bash
docker pull fayada/fastapi_calculator:latest
docker run -d -p 8000:8000 fayada/fastapi_calculator:latest
```

Then open http://localhost:8000 in your browser.

## Running the tests locally

Requirements: Python 3.12, Docker Desktop.

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Start a Postgres 16 database for the integration tests:

```bash
docker run -d --name test_postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=fastapi_db -p 5432:5432 postgres:16
```

4. Run the unit and integration tests:

```bash
pytest tests/unit tests/integration
```

The integration tests connect to `postgresql+psycopg2://postgres:postgres@localhost:5432/fastapi_db` by default. To use a different database, set the `DATABASE_URL` environment variable before running the tests.

To run the end-to-end browser tests, install the Playwright browser first:

```bash
playwright install chromium
pytest tests/e2e
```

When you're finished, stop the test database:

```bash
docker stop test_postgres
docker rm test_postgres
```

## Project structure

- `main.py`: FastAPI routes for the calculator
- `app/operations/`: arithmetic operations
- `app/logging_config.py`: logging setup
- `app/models.py`: SQLAlchemy `User` model
- `app/schemas.py`: Pydantic `UserCreate` and `UserRead` schemas
- `app/security.py`: bcrypt password hashing and verification
- `app/database.py`: database engine and session setup
- `tests/unit/`, `tests/integration/`, `tests/e2e/`: test suites
- `.github/workflows/test.yml`: GitHub Actions workflow that runs the tests on every push and pull request to `main`