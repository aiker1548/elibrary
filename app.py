from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Book, Author
from werkzeug.utils import secure_filename 
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os  # Для работы с файловой системой

app = Flask(__name__, static_folder='static')

# Подключаемся и создаем сессию базы данных
engine = create_engine('sqlite:///books-collections.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Главная страница
@app.route('/')
def index():
    books = session.query(Book).all()
    authors = session.query(Author).all()
    context = {
        "books": books,
        "authors": authors,
    }
    return render_template("index.html", context=context)



@app.route('/books/new/', methods=['GET', 'POST'])
def new_book():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = filename
        else:
            file_path = None

        newbook = Book(
            title=request.form['name'],
            genre=request.form['genre'],
            file_path=file_path
        )
        if request.form['author']:
            author = session.query(Author).filter_by(name=request.form['author']).first()
            if author:
                newbook.authors.append(author)
            else:
                author = Author(name=request.form['author'])
                newbook.authors.append(author)
        session.add(newbook)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newBook.html')



# Редактирование книги
@app.route("/books/<int:book_id>/edit/", methods=['GET', 'POST'])
def edit_book(book_id):
    edited_book = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['title']:
            edited_book.title = request.form['title']
        if request.form['genre']:
            edited_book.genre = request.form['genre']
        if request.files['file']:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            edited_book.file_path = os.path.join(UPLOAD_FOLDER, filename)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('editBook.html', book=edited_book)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_book(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# Удаление книги
@app.route('/books/<int:book_id>/delete/', methods=['GET', 'POST'])
def delete_book(book_id):
    book_to_delete = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(book_to_delete)
        session.commit()
        return redirect(url_for('index', book_id=book_id))
    else:
        return render_template('deleteBook.html', book=book_to_delete)


# Добавление автора
@app.route('/author/new/', methods=['GET', 'POST'])
def new_author():
    if request.method == 'POST':
        newauthor = Author(name=request.form['name'])
        session.add(newauthor)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newAuthor.html')


# Редактирование автора
@app.route("/author/<int:author_id>/edit/", methods=['GET', 'POST'])
def edit_author(author_id):
    edited_author = session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_author.name = request.form['name']
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('editAuthor.html', author=edited_author)


# Удаление автора
@app.route('/author/<int:author_id>/delete/', methods=['GET', 'POST'])
def delete_author(author_id):
    author_to_delete = session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        session.delete(author_to_delete)
        session.commit()
        return redirect(url_for('index', author_id=author_id))
    else:
        return render_template('deleteAuthor.html', author=author_to_delete)


# Функция для фильтрации книг
@app.route('/search/', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        if request.form['filter'] == 'book':
            books = session.query(Book).filter_by(title=request.form['title']).all()
        elif request.form['filter'] == 'author':
            books = session.query(Book).filter(Book.authors.any(Author.name.in_([request.form['title']]))).all()
    return render_template('searchResult.html', books=books)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
