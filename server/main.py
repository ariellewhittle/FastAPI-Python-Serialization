"""In-memory book API for the FastAPI mini-lab."""
import secrets
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

security = HTTPBasic()


def authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """Validate the demonstration credentials for every book endpoint."""
    user_ok = secrets.compare_digest(credentials.username.encode(), b"admin")
    password_ok = secrets.compare_digest(credentials.password.encode(), b"secret")
    if not (user_ok and password_ok):
        raise HTTPException(401, "Invalid credentials", headers={"WWW-Authenticate": "Basic"})
    return credentials.username


app = FastAPI(title="Book Management API", dependencies=[Depends(authenticate)])


class Author(BaseModel):
    name: str
    email: str | None = None


class Book(BaseModel):
    id: int = Field(gt=0)
    title: str
    author: Author
    year: int
    genre: str
    ratings: list[int] = Field(default_factory=list)


class BookPatch(BaseModel):
    title: str | None = None
    author: Author | None = None
    year: int | None = None
    genre: str | None = None
    ratings: list[int] | None = None


books = [
    Book(id=1, title="The Great Gatsby", author=Author(
        name="F. Scott Fitzgerald", email="fscott@example.com"),
        year=1925, genre="Fiction"),
    Book(id=2, title="1984", author=Author(name="George Orwell"),
         year=1949, genre="Dystopian"),
]


def find_index(book_id: int) -> int:
    for index, book in enumerate(books):
        if book.id == book_id:
            return index
    raise HTTPException(404, "Book not found")


@app.get("/books", response_model=list[Book])
def list_books():
    return books


# Register fixed paths before the dynamic book ID path.
@app.get("/books/count")
def count_books():
    return {"count": len(books)}


@app.get("/books/genre/{genre}", response_model=list[Book])
def search_genre(genre: str):
    return [book for book in books if book.genre.casefold() == genre.casefold()]


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    return books[find_index(book_id)]


@app.post("/books", response_model=Book, status_code=201)
def create_book(book: Book):
    if any(existing.id == book.id for existing in books):
        raise HTTPException(400, "Book ID already exists")
    books.append(book)
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book):
    index = find_index(book_id)
    if book.id != book_id:
        raise HTTPException(400, "Body ID must match URL ID")
    books[index] = book
    return book


@app.patch("/books/{book_id}", response_model=Book)
def patch_book(book_id: int, changes: BookPatch):
    index = find_index(book_id)
    # Omitted or null fields remain unchanged; an empty ratings list clears it.
    data = books[index].model_dump()
    data.update(changes.model_dump(exclude_none=True, exclude_unset=True))
    books[index] = Book(**data)
    return books[index]


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    books.pop(find_index(book_id))
    return {"message": "Book deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
