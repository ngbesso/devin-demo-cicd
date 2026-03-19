# Task Manager API

A simple FastAPI task management application.

## Features

- Create, read, update, delete tasks
- Priority levels (low, medium, high)
- Task completion tracking
- Input validation and error handling

## Setup

```bash
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration. The pipeline runs automatically on every push and pull request.

| Job | Tool | Description |
|-----|------|-------------|
| **Lint** | [Ruff](https://docs.astral.sh/ruff/) | Checks code style and runs formatter verification |
| **Test** | [Pytest](https://docs.pytest.org/) | Runs the full test suite |
| **Security** | [pip-audit](https://pypi.org/project/pip-audit/) | Scans dependencies for known vulnerabilities |
| **Dependency Check** | Custom script | Reports on dependency freshness |
