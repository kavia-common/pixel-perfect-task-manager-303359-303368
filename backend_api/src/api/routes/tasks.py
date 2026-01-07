from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.api.db import get_db
from src.api.models import Task, TaskPriority, TaskStatus
from src.api.schemas import TaskCompleteToggle, TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get(
    "",
    response_model=List[TaskOut],
    summary="List tasks",
    description="List tasks with optional filters: status and search (title/description).",
    operation_id="list_tasks",
)
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(
        None, alias="status", description="Filter by status: todo|in_progress|done."
    ),
    search: Optional[str] = Query(
        None,
        description="Search substring against title and description (case-insensitive).",
    ),
    db: Session = Depends(get_db),
) -> List[Task]:
    stmt = select(Task)

    if status_filter is not None:
        stmt = stmt.where(Task.status == TaskStatus(status_filter))

    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Task.title.ilike(like), Task.description.ilike(like)))

    stmt = stmt.order_by(Task.created_at.desc())
    return list(db.execute(stmt).scalars().all())


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task.",
    operation_id="create_task",
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    task = Task(
        title=payload.title,
        description=payload.description,
        status=TaskStatus(payload.status),
        priority=TaskPriority(payload.priority),
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get task",
    description="Fetch a task by id.",
    operation_id="get_task",
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    return _get_task_or_404(db, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Replace task fields (full update).",
    operation_id="update_task",
)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = _get_task_or_404(db, task_id)
    task.title = payload.title
    task.description = payload.description
    task.status = TaskStatus(payload.status)
    task.priority = TaskPriority(payload.priority)
    task.due_date = payload.due_date
    task.touch_updated_at()

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskOut,
    summary="Toggle/set completion",
    description="Toggle task completion (status=done) or set it explicitly via body {completed: true/false}.",
    operation_id="toggle_task_complete",
)
def toggle_task_complete(
    task_id: int,
    payload: TaskCompleteToggle,
    db: Session = Depends(get_db),
) -> Task:
    task = _get_task_or_404(db, task_id)

    if payload.completed is None:
        task.status = TaskStatus.done if task.status != TaskStatus.done else TaskStatus.todo
    else:
        task.status = TaskStatus.done if payload.completed else TaskStatus.todo

    task.touch_updated_at()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by id.",
    operation_id="delete_task",
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = _get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
    return None
