from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                media TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                comment TEXT,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        ''')
        conn.commit()

# Check if uploaded file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page: list all posts
@app.route('/')
def index():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = c.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Add new post (GET: form, POST: submit)
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        media = request.files.get('media')
        filename = None

        if media and allowed_file(media.filename):
            filename = secure_filename(media.filename)
            media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, media) VALUES (?, ?, ?)', (title, content, filename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add.html')

# View a single post and its comments
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    if request.method == 'POST':
        comment = request.form['comment']
        c.execute('INSERT INTO comments (post_id, comment) VALUES (?, ?)', (post_id, comment))
        conn.commit()

    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()

    c.execute('SELECT comment FROM comments WHERE post_id = ?', (post_id,))
    comments = c.fetchall()

    conn.close()
    return render_template('post.html', post=post, comments=comments)

# Delete a post and associated media/comments
@app.route('/delete/<int:post_id>')
def delete(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    c.execute('SELECT media FROM posts WHERE id = ?', (post_id,))
    media_file = c.fetchone()
    if media_file and media_file[0]:
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_file[0])
        if os.path.exists(media_path):
            os.remove(media_path)

    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    c.execute('DELETE FROM comments WHERE post_id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
