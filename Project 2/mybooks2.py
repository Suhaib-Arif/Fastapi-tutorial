from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Book:
    id: str
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(title="ID Not Required")
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str  = Field(min_length=3, max_length=100)
    rating: int = Field(gt=0, lt=10)
    published_date: int = 2012

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'codingwithroby',
                'description': 'A new description of a book',
                'rating': 5,
                'published_date': 2029
            }
        }


BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5,63543),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5,63543),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5,63543),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2,63543),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3,63543),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1,63543)
]



@app.get('/read_books/')
async def read_books():
    return BOOKS


@app.get('/get_book_id/{book_id}')
async def read_books(book_id: int = Path(gt=0)):
    
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(detail="Item is Not found", status_code=404)

@app.get('/get_book_rating/')
async def read_books(book_rating: int = Query(gt=1, lt = 100)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    
    return books_to_return


@app.put('/update_book/')
async def update_book_data(Book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == Book.id:
            BOOKS[i] = Book
            return 

    raise HTTPException(status_code=404, detail="Item Not Found") 

@app.delete('/delete_book/')
async def delete_book_data(Book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == Book_id:
            BOOKS.pop(i) 
            return 

    raise HTTPException(status_code=404, detail="Item Not Found") 


@app.post('/create_book/')
async def create_book(BookData: BookRequest):
    
    new_book = Book(**BookData.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    book.id = BOOKS[-1].id + 1 if BOOKS else 1
    return book


