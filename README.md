# FastAPI Calculator

A FastAPI calculator web app with add, subtract, multiply, and divide operations, request logging, a browser interface, user registration and login with hashed passwords, and calculation storage in PostgreSQL.

## Docker Hub

Image: https://hub.docker.com/r/fayada/fastapi_calculator

Pull and run it:

```bash
docker pull fayada/fastapi_calculator:latest
docker run -d -p 8000:8000 fayada/fastapi_calculator:latest
```

Then open http://localhost:8000 in your browser.

## API endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/users/register` | Create a user (username, email, password). Returns the user without the password. |
| POST | `/users/login` | Check a username and password against the stored hash. |
| GET | `/calculations` | List all saved calculations. |
| GET | `/calculations/{id}` | Get one calculation. |
| POST | `/calculations` | Compute and save a calculation (`type` is Add, Sub, Multiply, or Divide). |
| PUT | `/calculations/{id}` | Change a saved calculation and recompute it. |
| DELETE | `/calculations/{id}` | Delete a saved calculation. |
| POST | `/add`, `/subtract`, `/multiply`, `/divide` | The original calculator operations, which return the result only. |

## Checking the endpoints manually

1. Start the app locally with `python main.py`, or run the Docker image.
2. Open http://localhost:8000/docs in your browser.
3. Expand an endpoint, click **Try it out**, enter the request body, and click **Execute**.

For example, to create a calculation, use `POST /calculations` with this body:

```json
{ "a": 6, "b": 3, "type": "Divide" }
```

The response should include `"result": 2.0`.

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

The integration tests cover:
- **User routes** (`tests/integration/test_user_routes.py`): registration, duplicate and invalid input, password hashing, and login.
- **Calculation routes** (`tests/integration/test_calculation_routes.py`): create, browse, read, edit, and delete, plus errors such as a missing calculation, an unknown type, and a zero divisor.

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

## Known vulnerabilities

The CI pipeline runs a Trivy scan on the Docker image before it pushes to Docker Hub. The scan fails on CRITICAL or HIGH findings that have a fix available. Six findings are accepted for now and listed in `.trivyignore`:

| CVE | Package | Reason |
|---|---|---|
| CVE-2026-63374 | anyio 4.6.2.post1 (CRITICAL) | Upgrading to 4.14.2 breaks the browser (e2e) test |
| CVE-2025-43859 | h11 0.14.0 | Fix needs httpcore upgraded with it |
| CVE-2025-47273 | setuptools 70.3.0 | Comes from the base Python image |
| CVE-2025-62727 | starlette 0.41.2 | Fix needs fastapi upgraded with it |
| CVE-2026-48818 | starlette 0.41.2 | Fix needs fastapi upgraded with it |
| CVE-2026-54283 | starlette 0.41.2 | Fix needs fastapi upgraded with it |

These are planned for a later update, which will upgrade `starlette` and `fastapi` together, pair `h11` with `httpcore`, and resolve the `anyio` browser test failure. The divide-by-zero browser test is skipped in CI (`-k "not divide_by_zero"`) until that is fixed; the same behavior is covered by the unit and integration tests.

## Project structure

- `main.py`: FastAPI app, including the calculator routes and the user and calculation routers
- `app/operations/`: arithmetic operations
- `app/calculation_factory.py`: maps Add, Sub, Multiply, and Divide to their operations
- `app/calculation_routes.py`: calculation BREAD endpoints
- `app/user_routes.py`: user register and login endpoints
- `app/logging_config.py`: logging setup
- `app/models.py`: SQLAlchemy `User` and `Calculation` models
- `app/schemas.py`: Pydantic `UserCreate`, `UserRead`, `CalculationCreate`, and `CalculationRead` schemas
- `app/security.py`: bcrypt password hashing and verification
- `app/database.py`: database engine and session setup
- `tests/unit/`, `tests/integration/`, `tests/e2e/`: test suites
- `.github/workflows/test.yml`: GitHub Actions workflow that runs the tests on every push and pull request to `main`, scans the image with Trivy, then pushes the Docker image after the tests and scan pass
- `.trivyignore`: accepted Trivy findings, with reasons in the README