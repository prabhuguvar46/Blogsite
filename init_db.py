import sqlite3

conn = sqlite3.connect('blog.db')
c = conn.cursor()

c.execute('''
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    media TEXT
)
''')

c.execute('''
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id)
)
''')

conn.commit()
conn.close()
print("Database initialized with media column.")
