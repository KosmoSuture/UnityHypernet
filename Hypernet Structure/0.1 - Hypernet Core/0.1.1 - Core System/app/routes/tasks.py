"""
Tasks Routes

Endpoints for managing tasks and to-do items.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task

router = APIRouter()


# Request/Response Models
class TaskCreate(BaseModel):
    """Task creation request"""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    status: str = Field(default='pending', description="pending, in_progress, completed, cancelled")
    priority: Optional[str] = Field(None, description="low, medium, high, urgent")
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[UUID] = None
    tags: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    """Task update request"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[UUID] = None
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Task response"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    due_at: Optional[datetime]
    completed_at: Optional[datetime]
    parent_task_id: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Paginated task list response"""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task.

    - **title**: Task title (required)
    - **description**: Task details
    - **status**: pending, in_progress, completed, cancelled
    - **priority**: low, medium, high, urgent
    - **due_at**: Due date/time
    - **parent_task_id**: Parent task for subtasks
    """
    task = Task(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        status=request.status,
        priority=request.priority,
        due_at=request.due_at,
        completed_at=request.completed_at,
        parent_task_id=request.parent_task_id,
        tags=request.tags
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    overdue: Optional[bool] = Query(None, description="Show only overdue tasks"),
    parent_only: Optional[bool] = Query(None, description="Show only top-level tasks"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks for the current user.

    Supports:
    - Filter by status (pending, in_progress, completed, cancelled)
    - Filter by priority (low, medium, high, urgent)
    - Filter by tag
    - Show only overdue tasks
    - Show only parent tasks (no subtasks)
    - Pagination

    Results ordered by priority (urgent first), then due_at.
    """
    query = db.query(Task).filter(
        and_(
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    )

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if tag:
        query = query.filter(Task.tags.contains([tag]))

    if overdue:
        now = datetime.utcnow()
        query = query.filter(
            and_(
                Task.due_at < now,
                Task.status.in_(['pending', 'in_progress'])
            )
        )

    if parent_only:
        query = query.filter(Task.parent_task_id.is_(None))

    total = query.count()

    # Custom ordering: urgent > high > medium > low, then by due_at
    offset = (page - 1) * page_size
    items = query.order_by(
        Task.priority.desc().nullslast(),
        Task.due_at.asc().nullslast()
    ).offset(offset).limit(page_size).all()

    return TaskListResponse(
        items=[TaskResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID."""
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)


@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
async def get_subtasks(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all subtasks for a parent task.

    Returns tasks where parent_task_id equals the given task_id.
    """
    # Verify parent task exists and belongs to user
    parent_task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found"
        )

    # Get subtasks
    subtasks = db.query(Task).filter(
        and_(
            Task.parent_task_id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).all()

    return [TaskResponse.model_validate(task) for task in subtasks]


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    request: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task.

    All fields are optional. Only provided fields will be updated.
    """
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.status is not None:
        task.status = request.status
        # Auto-set completed_at when marking as completed
        if request.status == 'completed' and task.completed_at is None:
            task.completed_at = datetime.utcnow()
    if request.priority is not None:
        task.priority = request.priority
    if request.due_at is not None:
        task.due_at = request.due_at
    if request.completed_at is not None:
        task.completed_at = request.completed_at
    if request.parent_task_id is not None:
        task.parent_task_id = request.parent_task_id
    if request.tags is not None:
        task.tags = request.tags

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a task as completed.

    Sets status to 'completed' and completed_at to current time.
    """
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = 'completed'
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a task."""
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.soft_delete()
    db.commit()

    return None
