from fastapi import FastAPI, HTTPException

from app.models import TaskCreate, TaskResponse, TaskUpdate

app = FastAPI(title="Task Manager API", version="1.0.0")

# In-memory task storage
tasks: dict[int, dict] = {}
next_id: int = 1


@app.get("/")
def root() -> dict:
    return {"name": "Task Manager API", "version": "1.0.0"}


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks() -> list[dict]:
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> dict:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate) -> dict:
    global next_id
    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": False,
    }
    tasks[next_id] = new_task
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate) -> dict:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    existing = tasks[task_id]
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        existing[key] = value

    return existing


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return {"detail": "Task deleted"}
