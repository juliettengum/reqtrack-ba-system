
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATABASE = Path(__file__).resolve().parent / "reqtrack.db"

TYPES = ("Functional", "Non-Functional")
PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Pending", "Approved", "Rejected")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def home():
    with get_db() as db:
        requirements = db.execute(
            "SELECT * FROM requirements ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "index.html",
        requirements=requirements,
        types=TYPES,
        priorities=PRIORITIES,
        statuses=STATUSES
    )


@app.route("/add", methods=["POST"])
def add_requirement():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    req_type = request.form.get("type", "")
    priority = request.form.get("priority", "")

    if (
        not title or not description
        or req_type not in TYPES
        or priority not in PRIORITIES
    ):
        return "Invalid requirement information", 400

    with get_db() as db:
        db.execute(
            """
            INSERT INTO requirements
            (title, description, type, priority, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description, req_type, priority, "Pending")
        )

    return redirect(url_for("home"))


@app.route("/status/<int:req_id>", methods=["POST"])
def update_status(req_id):
    status = request.form.get("status", "")

    if status not in STATUSES:
        return "Invalid status", 400

    with get_db() as db:
        result = db.execute(
            "UPDATE requirements SET status = ? WHERE id = ?",
            (status, req_id)
        )

        if result.rowcount == 0:
            return "Requirement not found", 404

    return redirect(url_for("home"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
