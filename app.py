from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("expenses.db")

@app.route("/", methods=["GET","POST"])
def index():
    conn = db()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        category TEXT,
        amount REAL,
        date TEXT)""")

    if request.method == "POST":
        cur.execute("INSERT INTO expenses VALUES(NULL,?,?,?,?)",
        (request.form["description"],
         request.form["category"],
         request.form["amount"],
         request.form["date"]))
        conn.commit()
        return redirect("/")

    start = request.args.get("start")
    end = request.args.get("end")
    cat = request.args.get("category")

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if start:
        query += " AND date>=?"
        params.append(start)
    if end:
        query += " AND date<=?"
        params.append(end)
    if cat and cat!="All":
        query += " AND category=?"
        params.append(cat)

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0] or 0

    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    cats = cur.fetchall()

    cur.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date")
    dates = cur.fetchall()

    conn.close()
    return render_template("index.html",
        expenses=rows, total=total,
        cats=cats, dates=dates)

@app.route("/delete/<int:id>")
def delete(id):
    conn=db();cur=conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit();conn.close()
    return redirect("/")

if __name__ == "__main__":
    print("Starting production server...")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)