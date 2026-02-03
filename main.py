from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Book CRUD API")

class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float
    published_year: int

books_db: List[Book] = []

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: Book):
    for b in books_db:
        if b.id == book.id:
            raise HTTPException(status_code=400, detail="Book ID already exists")
    books_db.append(book)
    return book

@app.get("/books", response_model=List[Book])
def get_books(author: Optional[str] = None):
    if author:
        return [book for book in books_db if book.author.lower() == author.lower()]
    return books_db


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):
    for index, book in enumerate(books_db):
        if book.id == book_id:
            books_db[index] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            books_db.remove(book)
            return
    raise HTTPException(status_code=404, detail="Book not found")
