from flask import Flask, render_template, request, redirect, url_for, session 
import joblib
import sqlite3
import numpy as np

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Load ML model
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
label_encoders = joblib.load("label_encoders.pkl")

def preprocess_input(data):
    data["Gender"] = label_encoders["Gender"].transform([data["Gender"]])[0]
    input_data = np.array([[
        data["Age"], data["Gender"], data["GPA"], data["Course_Load"],
        data["Sleep_Hours"], data["Exercise_Hours"], data["Social_Activity"]
    ]])
    return scaler.transform(input_data)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect(url_for("predict"))
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        form_data = {
            "Age": int(request.form["age"]),
            "Gender": request.form["gender"],
            "GPA": float(request.form["gpa"]),
            "Course_Load": int(request.form["course_load"]),
            "Sleep_Hours": float(request.form["sleep_hours"]),
            "Exercise_Hours": float(request.form["exercise_hours"]),
            "Social_Activity": int(request.form["social_activity"]),
        }
        processed_data = preprocess_input(form_data)
        prediction = model.predict(processed_data)[0]
        result = label_encoders["Mental_Health"].inverse_transform([prediction])[0]
        return render_template("index.html", result=result)
    return render_template("index.html", result=None)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ✅ Render-compatible Flask launch
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
