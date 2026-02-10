"""
Transactions API Routes

Provides CRUD operations for financial transaction management including
payments, purchases, transfers, and other financial activities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction


router = APIRouter()


# Pydantic Models for Request/Response
class TransactionCreate(BaseModel):
    transaction_type: str = Field(..., description="purchase, payment, transfer, refund, subscription, income, other")
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field(default="USD", max_length=3)
    merchant: Optional[str] = Field(None, max_length=300)
    category: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    transaction_date: datetime
    payment_method: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="completed", description="pending, completed, failed, cancelled, refunded")
    account_last_four: Optional[str] = Field(None, max_length=4)
    receipt_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_recurring: bool = Field(default=False)
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    category: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, description="pending, completed, failed, cancelled, refunded")
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    transaction_type: str
    amount: Decimal
    currency: str
    merchant: Optional[str]
    category: Optional[str]
    description: Optional[str]
    transaction_date: datetime
    payment_method: Optional[str]
    status: str
    account_last_four: Optional[str]
    receipt_url: Optional[str]
    tags: List[str]
    is_recurring: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    pages: int
    total_amount: Optional[Decimal] = None


class SpendingSummary(BaseModel):
    category: str
    total: Decimal
    count: int
    currency: str


# Endpoints
@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction record."""
    transaction = Transaction(
        user_id=current_user.id,
        **transaction_data.dict()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    merchant: Optional[str] = Query(None, description="Filter by merchant"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_recurring: Optional[bool] = Query(None, description="Filter recurring transactions"),
    min_amount: Optional[Decimal] = Query(None, description="Minimum amount"),
    max_amount: Optional[Decimal] = Query(None, description="Maximum amount"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in merchant, description, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List transactions with optional filtering and totals."""
    query = db.query(Transaction).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None)
        )
    )

    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    if category:
        query = query.filter(Transaction.category == category)

    if merchant:
        query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))

    if status:
        query = query.filter(Transaction.status == status)

    if is_recurring is not None:
        query = query.filter(Transaction.is_recurring == is_recurring)

    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.combine(end_date, datetime.max.time()))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.merchant.ilike(search_pattern),
                Transaction.description.ilike(search_pattern),
                Transaction.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Calculate total amount for filtered transactions
    from sqlalchemy import func
    total_amount_result = query.with_entities(func.sum(Transaction.amount)).scalar()
    total_amount = total_amount_result if total_amount_result else Decimal(0)

    # Order by transaction_date descending (most recent first)
    query = query.order_by(Transaction.transaction_date.desc())

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return TransactionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        total_amount=total_amount
    )


@router.get("/summary", response_model=List[SpendingSummary])
async def get_spending_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get spending summary grouped by category."""
    from sqlalchemy import func

    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count'),
        Transaction.currency
    ).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None),
            Transaction.category.isnot(None)
        )
    )

    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.combine(end_date, datetime.max.time()))

    results = query.group_by(Transaction.category, Transaction.currency).all()

    return [
        SpendingSummary(
            category=row.category,
            total=row.total,
            count=row.count,
            currency=row.currency
        )
        for row in results
    ]


@router.get("/categories", response_model=List[str])
async def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique categories for user's transactions."""
    categories = db.query(Transaction.category).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None),
            Transaction.category.isnot(None)
        )
    ).distinct().all()

    return [cat[0] for cat in categories if cat[0]]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific transaction by ID."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None)
        )
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transaction's metadata."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None)
        )
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    update_data = transaction_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    transaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
            Transaction.deleted_at.is_(None)
        )
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    transaction.deleted_at = datetime.utcnow()
    db.commit()

    return None
