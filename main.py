from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
import time

from database import engine, get_session
from models import User, UserCreate, Book
from auth import hash_password, verify_password, create_access_token
from jose import JWTError, jwt

app = FastAPI(title="Book API with JWT Authentication")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

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

def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):

    hashed_pw = hash_password(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):

    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: Book,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):

    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books", response_model=List[Book])
def get_books(author: Optional[str] = None,
              session: Session = Depends(get_session)):

    query = select(Book)
    if author:
        query = query.where(Book.author == author)

    return session.exec(query).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int,
             session: Session = Depends(get_session)):

    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int,
                updated_book: Book,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):

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
def delete_book(book_id: int,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):

    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
