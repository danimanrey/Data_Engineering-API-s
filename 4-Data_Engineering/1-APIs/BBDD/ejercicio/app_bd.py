import json
from flask import Flask, request, jsonify
import sqlite3
import os

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def hello():
    return "Bienvenido a mi API sobre libros"

# 0.Ruta para obtener todos los libros

@app.route('/libros', methods=['GET'])
def get_all_books():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()
    return jsonify({'books': books})

# 1.Ruta para obtener el conteo de libros por autor ordenados de forma descendente

@app.route('/conteo_libros_por_autor', methods=['GET'])
def conteo_libros_por_autor():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT author, COUNT(*) as conteo FROM books GROUP BY author ORDER BY conteo DESC')
    books = cursor.fetchall()
    conn.close()
    lista_resultados = [{'autor': autor, 'conteo': conteo} for autor, conteo in books]

    return jsonify({'conteo_libros_por_autor': lista_resultados})

# 2.Ruta para obtener los libros de un autor como argumento en la llamada

@app.route('/libros_por_autor', methods=['GET'])
def obtener_libros_por_autor():
    author = request.args.get('author')
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM books WHERE author = ?', (author,))
    books = cursor.fetchall()
    conn.close()

    libros_por_autor = [{'titulo': books['title'], 'autor': books['author']} for book in books]

    return jsonify({'libros_por_autor': libros_por_autor})


# 3.Ruta para obtener los libros filtrados por título, publicación y autor

@app.route('/libros_filtrados', methods=['GET'])
def libros_filtrados():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    title = request.args.get("title")
    published = request.args.get('published')
    author = request.args.get('author')
    cursor.execute("SELECT * FROM books WHERE title = ? AND published = ? AND author = ?;", (title, published, author))
    libros_filtrados = cursor.fetchall()
    conn.close()


    return jsonify(libros_filtrados)


app.run()