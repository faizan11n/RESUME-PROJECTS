import os
import time
import pymysql
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Database connection settings (read from environment variables, set in docker-compose.yaml)
DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "demouser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "demopass123")
DB_NAME = os.environ.get("DB_NAME", "notesapp")


def get_connection():
    """Create a new database connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


def wait_for_db_and_init():
    """Retry connecting to the DB until it's ready, then create the table if needed."""
    for attempt in range(15):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        content VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()
            conn.close()
            print("Database ready and table ensured.")
            return
        except Exception as e:
            print(f"Waiting for database... ({attempt + 1}/15) - {e}")
            time.sleep(3)
    raise Exception("Could not connect to the database after multiple attempts.")


PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>One-Page Notes App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #2a5298; margin-bottom: 20px; }
        form { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type=text] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        button {
            background: #2a5298;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover { background: #1e3c72; }
        ul { list-style: none; padding: 0; }
        li {
            background: #eef2ff;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .timestamp { font-size: 12px; color: #888; }
        .empty { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>My Notes (stored in MySQL)</h1>
        <form method="POST" action="/add">
            <input type="text" name="content" placeholder="Write a note..." required>
            <button type="submit">Add</button>
        </form>
        <ul>
            {% for note in notes %}
                <li>
                    <span>{{ note.content }}</span>
                    <span class="timestamp">{{ note.created_at }}</span>
                </li>
            {% else %}
                <li class="empty">No notes yet. Add one above!</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        notes = cursor.fetchall()
    conn.close()
    return render_template_string(PAGE_TEMPLATE, notes=notes)


@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content", "").strip()
    if content:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        conn.commit()
        conn.close()
    return redirect("/")


if __name__ == "__main__":
    wait_for_db_and_init()
    app.run(host="0.0.0.0", port=5000)
