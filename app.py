from flask import Flask, render_template, request, redirect
import sqlite3
app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
        """)

    conn.commit()
    conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            return redirect("/")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"

    return render_template("register.html")

@app.route("/")
def home():
    conn = get_db()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()
    total_students=len(students)
    
    conn.close()
    return render_template("index.html",students=students, total_students=total_students)
                            


@app.route("/add", methods=["POST"])
def add_student():

    name = request.form["name"]
    roll_no = request.form["roll_no"]
    course = request.form["course"]

    conn = get_db()

    conn.execute("""
        INSERT INTO students (name, roll_no, course)
        VALUES (?, ?, ?)
    """, (name, roll_no, course))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete_student(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]

        conn.execute(
            "UPDATE students SET name = ?, roll_no = ?, course = ? WHERE id = ?",
            (name, roll_no, course, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", student=student)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)