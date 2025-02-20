from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
DATABASE_URL = "postgresql://bookmark_user:bookmark_password@db:5432/bookmark_manager"


def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
    return conn


# @app.route('/db_test')
# def db_test():
#     conn = get_db_connection()
#     if conn:
#         conn.close()
#         return "success!"
#     else:
#         return "failed"


@app.route('/')
def index():
    bookmarks = get_all_bookmarks()
    return render_template("index.html", bookmarks=bookmarks)


@app.route('/add_bookmark', methods=['GET', 'POST'])
def add_bookmark():
    message = None
    if request.method == "POST":
        url = request.form['url']
        title = request.form['title']
        tags = request.form['tags']
        if create_bookmark(url, title, tags):
            message = "Bookmark added!"
        else:
            message = "Error adding bookmark. Please try again."
    return render_template('add_bookmark.html', message=message)


# @app.route('/test_bookmarks')
# def test_bookmarks():
#     bookmarks = get_all_bookmarks()
#     return str(bookmarks)


def create_bookmark(url, title, tags):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO bookmarks (url, title, tags) VALUES (%s, %s, %s)", (url, title, tags))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except psycopg2.Error as e:
            print(f"Database error inserting bookmark: {e}")
            conn.rollback()
            cur.close()
            conn.close()
            return False
    return False


def get_all_bookmarks():
    conn = get_db_connection()
    bookmarks = []
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, url, title, tags, created_at FROM bookmarks ORDER BY created_at DESC")
            rows = cur.fetchall()
            for row in rows:
                bookmark = {
                    "id": row[0],
                    "url": row[1],
                    "title": row[2],
                    "tags": row[3],
                    "created_at": row[4]
                }
                bookmarks.append(bookmark)
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database error fetching bookmarks: {e}")
            cur.close()
            conn.close()
    return bookmarks


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
