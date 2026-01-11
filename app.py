from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = "kanban.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            color TEXT NOT NULL
        )
        """)

import random

PASTEL_COLORS = [
    "#FFD6E0",  # pink
    "#E2F0CB",  # green
    "#CDE7F0",  # blue
    "#FFF1C1",  # yellow
    "#E6D9FF",  # purple
    "#D7F5E9",  # mint
]

def get_next_color():
    with db() as conn:
        last_colors = conn.execute(
            "SELECT color FROM tasks ORDER BY id DESC LIMIT 4"
        ).fetchall()

    used = {row["color"] for row in last_colors}
    available = [c for c in PASTEL_COLORS if c not in used]

    return random.choice(available if available else PASTEL_COLORS)


@app.route("/")
def index():
    with db() as conn:
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
    return render_template("kanban.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    status = request.form["status"]
    color = get_next_color()

    with db() as conn:
        conn.execute(
            "INSERT INTO tasks (title, status, color) VALUES (?, ?, ?)",
            (title, status, color)
        )
    return redirect(url_for("index"))


@app.route("/move", methods=["POST"])
def move():
    with db() as conn:
        conn.execute(
            "UPDATE tasks SET status=? WHERE id=?",
            (request.form["status"], request.form["id"])
        )
    return ("", 204)

@app.route("/delete/<int:id>")
def delete(id):
    with db() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
