from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    """Shared fields between task create/update models."""
    title: str = Field(..., min_length=1, max_length=200, description="Short task title.")
    description: Optional[str] = Field(None, description="Longer task details.")
    status: TaskStatus = Field("todo", description="Task status: todo|in_progress|done.")
    priority: TaskPriority = Field("medium", description="Task priority: low|medium|high.")
    due_date: Optional[date] = Field(None, description="Optional due date.")


class TaskCreate(TaskBase):
    """Request body for creating a task."""


class TaskUpdate(BaseModel):
    """Request body for full update of a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    due_date: Optional[date] = None


class TaskCompleteToggle(BaseModel):
    """Request body for toggling completion; if omitted, toggles current state."""
    completed: Optional[bool] = Field(
        None,
        description="If provided, sets done=true/false; if omitted, toggles.",
    )


class TaskOut(TaskBase):
    """Response model for a task."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique task id.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")
