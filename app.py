import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Session-kku thevayana secret key

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            priority TEXT,
            recurrence TEXT,
            alarm_sound TEXT,
            due_date TEXT,
            due_time TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    
    # Check if 'username' column exists in tasks table, if not, add it automatically!
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor.fetchall()]
    if "username" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN username TEXT")

    # Subtasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            flash("Username already exists! Choose another.", "danger")
            return redirect(url_for("signup"))
            
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("Signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
        
    username = session["username"]
    status_filter = request.args.get("status", "all")
    category_filter = request.args.get("category", "all")
    search_query = request.args.get("search", "")
    
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE username = ?"
    params = [username]
    
    if status_filter == "active":
        query += " AND completed = 0"
    elif status_filter == "completed":
        query += " AND completed = 1"
        
    if category_filter != "all":
        query += " AND category = ?"
        params.append(category_filter)
        
    if search_query:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    tasks_rows = cursor.fetchall()
    
    tasks = []
    for row in tasks_rows:
        task = dict(row)
        cursor.execute("SELECT * FROM subtasks WHERE task_id = ?", (task["id"],))
        task["subtasks"] = [dict(sub) for sub in cursor.fetchall()]
        tasks.append(task)
        
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE username = ?", (username,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE username = ? AND completed = 1", (username,))
    completed = cursor.fetchone()[0]
    conn.close()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    
    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        status_filter=status_filter,
        category_filter=category_filter,
        search_query=search_query,
        current_date=current_date,
        current_time=current_time,
        username=username,
    )

@app.route("/add_task", methods=["POST"])
def add_task():
    if "username" not in session:
        return redirect(url_for("login"))
        
    username = session["username"]
    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    priority = request.form.get("priority")
    recurrence = request.form.get("recurrence")
    alarm_sound = request.form.get("alarm_sound")
    due_date = request.form.get("due_date")
    due_time = request.form.get("due_time")
    subtask_titles = request.form.getlist("subtasks")
    
    if title:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (username, title, description, category, priority, recurrence, alarm_sound, due_date, due_time, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (username, title, description, category, priority, recurrence, alarm_sound, due_date, due_time),
        )
        task_id = cursor.lastrowid
        for sub_title in subtask_titles:
            if sub_title.strip():
                cursor.execute(
                    "INSERT INTO subtasks (task_id, title, completed) VALUES (?, ?, 0)",
                    (task_id, sub_title.strip()),
                )
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/toggle_task/<int:task_id>")
def toggle_task(task_id):
    if "username" not in session:
        return redirect(url_for("login"))
        
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM tasks WHERE id = ? AND username = ?", (task_id, session["username"]))
    row = cursor.fetchone()
    if row:
        new_status = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        cursor.execute("UPDATE subtasks SET completed = ? WHERE task_id = ?", (new_status, task_id))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit_task/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    if "username" not in session:
        return redirect(url_for("login"))
        
    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    priority = request.form.get("priority")
    recurrence = request.form.get("recurrence")
    alarm_sound = request.form.get("alarm_sound")
    due_date = request.form.get("due_date")
    due_time = request.form.get("due_time")
    
    if title:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tasks SET title = ?, description = ?, category = ?, priority = ?, recurrence = ?, alarm_sound = ?, due_date = ?, due_time = ?
            WHERE id = ? AND username = ?
            """,
            (title, description, category, priority, recurrence, alarm_sound, due_date, due_time, task_id, session["username"]),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    if "username" not in session:
        return redirect(url_for("login"))
        
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, session["username"]))
    cursor.execute("DELETE FROM subtasks WHERE task_id IN (SELECT id FROM tasks WHERE id = ?)", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)