from flask import Flask, render_template, request, redirect, session
import sqlite3, random
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this"
DB = "kanban.db"
PASSWORD_HASH = generate_password_hash("secret123")

COLORS = ["#FFD6E0","#E2F0CB","#CDE7F0","#FFF1C1","#E6D9FF","#D7F5E9"]

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,title TEXT,status TEXT,color TEXT)""")

def auth(f):
    @wraps(f)
    def w(*a,**k):
        return f(*a,**k) if session.get("auth") else redirect("/login")
    return w

def next_color():
    with db() as c:
        used = {r["color"] for r in c.execute(
            "SELECT color FROM tasks ORDER BY id DESC LIMIT 4")}
    return random.choice([c for c in COLORS if c not in used] or COLORS)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST" and check_password_hash(
        PASSWORD_HASH, request.form["password"]):
        session["auth"]=1
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
@auth
def index():
    with db() as c:
        t=c.execute("SELECT * FROM tasks").fetchall()
    return render_template("kanban.html", tasks=t)

@app.route("/add", methods=["POST"])
@auth
def add():
    with db() as c:
        c.execute("INSERT INTO tasks VALUES(NULL,?,?,?)",
        (request.form["title"],request.form["status"],next_color()))
    return redirect("/")

@app.route("/move", methods=["POST"])
@auth
def move():
    with db() as c:
        c.execute("UPDATE tasks SET status=? WHERE id=?",
        (request.form["status"],request.form["id"]))
    return ("",204)

@app.route("/delete/<int:i>")
@auth
def delete(i):
    with db() as c:
        c.execute("DELETE FROM tasks WHERE id=?", (i,))
    return redirect("/")

if __name__=="__main__":
    init_db()
    app.run("0.0.0.0",5000)