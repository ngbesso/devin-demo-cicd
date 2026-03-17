import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks


@pytest.fixture(autouse=True)
def reset_state():
    """Reset the in-memory state before each test."""
    global next_id
    tasks.clear()
    import app.main

    app.main.next_id = 1
    yield
    tasks.clear()
    app.main.next_id = 1


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Task Manager API"
    assert data["version"] == "1.0.0"


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Test task", "description": "A test", "priority": "high"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "A test"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert data["id"] == 1


def test_create_task_default_priority(client):
    response = client.post("/tasks", json={"title": "Simple task"})
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "medium"


def test_create_task_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task(client):
    client.post("/tasks", json={"title": "My task"})
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "My task"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task(client):
    client.post("/tasks", json={"title": "Original"})
    response = client.put("/tasks/1", json={"title": "Updated", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_task(client):
    client.post("/tasks", json={"title": "To delete"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    # Verify it's gone
    response = client.get("/tasks/1")
    assert response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
