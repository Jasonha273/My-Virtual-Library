from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT NOT NULL,
            pages INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/books', methods=['GET'])
def api_get_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, author, status, pages FROM books')
    rows= cursor.fetchall()
    conn.close()

    books = []
    for row in rows:
        book = {
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'status': row[3],
            'pages': row[4]
        }
        books.append(book)
    return jsonify(books)

@app.route('/books', methods=['POST'])
def api_add_book():
    #JSON data sent in the request body
    data= request.get_json()
    title = data.get('title').title() if data.get('title') else ''
    author = data.get('author').title() if data.get('author') else ''
    status = data.get('status').title() if data.get('status') else ''
    pages = data.get('pages')


    #connect to the database and insert the new book
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    #check for duplicate book title and author
    cursor.execute('SELECT * FROM books WHERE title = ? AND author = ?', (title, author))
    existing_book = cursor.fetchone()
    if existing_book:
        conn.close()
        return jsonify({'message': 'Book already exists'}), 400

    #Insert the new book into the database (Stray comma removed!)
    cursor.execute('''
        INSERT INTO books (title, author, status, pages) 
        VALUES (?, ?, ?, ?)
    ''', (title, author, status, pages))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book added successfully'}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def api_update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    status = data.get('status')
    pages = data.get('pages')

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE books
        SET title = ?, author = ?, status = ?, pages = ?
        WHERE id = ?
    ''', (title, author, status, pages, book_id))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Book updated successfully'}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))

    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return jsonify({'message': 'Book not found'}), 404
    return jsonify({'message': 'Book deleted successfully'}), 200

if __name__ == '__main__':
    init_db()  
    app.run(debug=True)