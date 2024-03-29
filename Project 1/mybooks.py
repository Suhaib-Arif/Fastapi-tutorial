from fastapi import FastAPI, Body

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get("/all_books")
async def read_all_books():
    return BOOKS


@app.get('/books/{dynamic_param}')
async def read_book(dynamic_param: str):
    for book in BOOKS:
        if book['title'].casefold() == dynamic_param.casefold():
            return book
        
@app.get('/books/')
async def read_by_category(category: str):
    books_to_return = []
    for book in BOOKS:
        if book['category'].casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return


@app.post('/books/create_book')
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put('/books/update_books')
async def update_book_data(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i]['title'].casefold() == updated_book['title'].casefold():
            BOOKS[i] = updated_book


@app.delete('/books/delete/{book_title}')
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i]['title'].casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

@app.get('/books_by_author/{author_name}/')
async def get_book_by_author(author_name: str, category: str):
    for book in BOOKS:
        if book.get('author').casefold() == author_name.casefold() and\
            book.get('category').casefold() == category.casefold():

            return book
