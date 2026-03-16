from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
import time

from database import engine, get_session
from models import Book

app = FastAPI(title="Book API with Middleware")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    print(
        f"PATH: {request.url.path} | "
        f"METHOD: {request.method} | "
        f"STATUS: {response.status_code} | "
        f"TIME: {process_time:.4f}s"
    )
    return response

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    print("Application started, database ready")

@app.on_event("shutdown")
def on_shutdown():
    print("Application shutting down")

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books", response_model=List[Book])
def get_books(author: Optional[str] = None, session: Session = Depends(get_session)):
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
def update_book(book_id: int, updated_book: Book, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = updated_book.title
    book.author = updated_book.author
    book.price = updated_book.price
    book.published_year = updated_book.published_year

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
