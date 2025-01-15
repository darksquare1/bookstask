from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db.database import get_db
from app.db import models
from app.api import schemas
from utils.security import RoleVerify

loan_router = APIRouter()


@loan_router.post('/borrow/{book_id}', response_model=schemas.BookLoanOut)
def borrow_book(book_id: int, db: Session = Depends(get_db),
                current_user: dict = Depends(RoleVerify(['reader', 'admin']))):
    user_id = db.query(models.User).filter(models.User.username == current_user.get('sub')).first().id
    user_loans = db.query(models.BookLoan).filter(models.BookLoan.user_id == user_id).all()
    if len(user_loans) >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can't borrow more than 5 books at the same time.")

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    if book.available_copies <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No available copies of the book.")

    estimated_return_date = date.today() + timedelta(days=14)

    new_loan = models.BookLoan(
        user_id=user_id,
        book_id=book.id,
        issue_date=date.today(),
        estimated_return_date=estimated_return_date,
        actual_return_date=None,
    )

    db.add(new_loan)
    db.commit()

    book.available_copies -= 1
    db.commit()

    return schemas.BookLoanOut(
        loan_id=new_loan.id,
        user_id=user_id,
        book_id=book.id,
        issue_date=new_loan.issue_date,
        estimated_return_date=new_loan.estimated_return_date,
        actual_return_date=None,
    )


@loan_router.post('/return/{loan_id}', response_model=schemas.BookLoanOut)
def return_book(loan_id: int, db: Session = Depends(get_db),
                current_user: dict = Depends(RoleVerify(['reader', 'admin']))):
    user_id = db.query(models.User).filter(models.User.username == current_user.get('sub')).first().id
    loan = db.query(models.BookLoan).filter(models.BookLoan.id == loan_id, models.BookLoan.user_id == user_id).first()

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Loan not found or this loan does not belong to you.")
    if loan.actual_return_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already returned this book')
    loan.actual_return_date = date.today()
    db.commit()

    book = db.query(models.Book).filter(models.Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found.")

    book.available_copies += 1
    db.commit()

    return schemas.BookLoanOut(
        loan_id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        issue_date=loan.issue_date,
        estimated_return_date=loan.estimated_return_date,
        actual_return_date=loan.actual_return_date,
    )


@loan_router.get('/my', response_model=list[schemas.BookLoanOut])
def get_my_loans(db: Session = Depends(get_db), current_user: dict = Depends(RoleVerify(['reader', 'admin']))):
    user_id = db.query(models.User).filter(models.User.username == current_user.get('sub')).first().id
    loans = db.query(models.BookLoan).filter(models.BookLoan.user_id == user_id).all()

    if not loans:
        raise HTTPException(status_code=404, detail="You have no borrowed books.")

    return [
        schemas.BookLoanOut(
            loan_id=loan.id,
            user_id=loan.user_id,
            book_id=loan.book_id,
            issue_date=loan.issue_date,
            estimated_return_date=loan.estimated_return_date,
            actual_return_date=loan.actual_return_date
        )
        for loan in loans
    ]


@loan_router.delete('/remove/{loan_id}', response_model=schemas.BookLoanOut)
def remove_loan(loan_id: int, db: Session = Depends(get_db),
                depdends_on: dict = Depends(RoleVerify(['admin']))):
    loan = db.query(models.BookLoan).filter(models.BookLoan.id == loan_id).first()

    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")

    book = db.query(models.Book).filter(models.Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found.")

    db.delete(loan)
    db.commit()

    book.available_copies += 1
    db.commit()

    return schemas.BookLoanOut(
        loan_id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        issue_date=loan.issue_date,
        estimated_return_date=loan.estimated_return_date,
        actual_return_date=loan.actual_return_date,
    )
