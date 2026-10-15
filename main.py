"""launchpad-api: a small, in-memory deployment demo."""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from itertools import count

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=80)


class Task(BaseModel):
    id: int
    title: str
    done: bool = False
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


tasks: dict[int, Task] = {}
task_ids = count(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global task_ids
    tasks.clear()
    task_ids = count(1)
    for title in (
        "Write the code",
        "Push to GitHub",
        "Deploy with Zynnode",
        "Celebrate",
    ):
        task = Task(id=next(task_ids), title=title)
        tasks[task.id] = task
    yield


app = FastAPI(title="launchpad-api", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "local"),
    }


@app.get("/api/tasks", response_model=list[Task])
async def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate) -> Task:
    task = Task(id=next(task_ids), title=payload.title)
    tasks[task.id] = task
    return task


def get_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{id}/toggle", response_model=Task)
async def toggle_task(id: int) -> Task:
    task = get_task(id)
    task.done = not task.done
    return task


@app.delete("/api/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int) -> Response:
    get_task(id)
    del tasks[id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats")
async def stats() -> dict[str, int]:
    total = len(tasks)
    done = sum(task.done for task in tasks.values())
    return {"total": total, "done": done, "remaining": total - done}
