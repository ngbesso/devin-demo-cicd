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

## Note

This project does not have CI/CD configured yet. It needs:
- Automated linting (ruff or flake8)
- Automated testing on push/PR
- Deployment pipeline
- Security vulnerability scanning
