from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------- LOGIN --------
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password))

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")


# -------- REGISTER --------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# -------- DASHBOARD --------
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    uid = session["user"]

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO expenses(user_id,title,category,amount,date) VALUES(?,?,?,?,?)",
        (uid,title,category,amount,date))

        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
    "SELECT id,title,category,amount,date FROM expenses WHERE user_id=?",
    (uid,))

    data = cur.fetchall()

    cur.execute(
    "SELECT SUM(amount) FROM expenses WHERE user_id=?",
    (uid,))

    total = cur.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",data=data,total=total)


# -------- DELETE EXPENSE --------
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)