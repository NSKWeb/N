import sqlite3
import string
from flask import Flask, render_template, request, redirect, g

app = Flask(__name__)
DATABASE = 'urls.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

BASE62 = string.ascii_letters + string.digits
def to_base62(n):
    if n == 0:
        return BASE62[0]
    arr = []
    base = len(BASE62)
    while n:
        n, rem = divmod(n, base)
        arr.append(BASE62[rem])
    arr.reverse()
    return ''.join(arr)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['url']
    if not long_url:
        return render_template('index.html', error="URL can't be empty.")

    db = get_db()

    # Check if the URL has already been shortened
    url_data = db.execute('SELECT short_code FROM urls WHERE long_url = ?', (long_url,)).fetchone()
    if url_data and url_data['short_code']:
        short_code = url_data['short_code']
    else:
        # Insert the new URL to get its ID
        cursor = db.execute('INSERT INTO urls (long_url, short_code) VALUES (?, ?)', (long_url, ''))
        db.commit()

        # Encode the ID to base62
        url_id = cursor.lastrowid
        short_code = to_base62(url_id)

        # Update the record with the short code
        db.execute('UPDATE urls SET short_code = ? WHERE id = ?', (short_code, url_id))
        db.commit()

    short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url)

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    db = get_db()
    url_data = db.execute('SELECT long_url FROM urls WHERE short_code = ?', (short_code,)).fetchone()

    if url_data:
        # Prepend http:// if no scheme is present to ensure the redirect works
        long_url = url_data['long_url']
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'http://' + long_url
        return redirect(long_url)
    else:
        return render_template('index.html', error='Short URL not found.'), 404

if __name__ == '__main__':
    # Initialize the database if it doesn't exist
    def setup_database():
        with app.app_context():
            db = get_db()
            # Check if the table exists
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
            if cursor.fetchone() is None:
                with app.open_resource('schema.sql', mode='r') as f:
                    db.cursor().executescript(f.read())
                db.commit()

    setup_database()
    app.run(debug=True, port=5001)
