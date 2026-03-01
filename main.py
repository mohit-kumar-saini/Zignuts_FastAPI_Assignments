from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Session, select
from typing import List, Optional

from database import engine, get_session
from models import Book

app = FastAPI(title="Book CRUD API with Database")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.get("/books", response_model=List[Book])
def get_books(
    author: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Book)
    if author:
        query = query.where(Book.author == author)
    return session.exec(query).all()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    updated_book: Book,
    session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = updated_book.title
    book.author = updated_book.author
    book.price = updated_book.price
    book.published_year = updated_book.published_year

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
