from flask import Flask, render_template, request, redirect, send_file
import sqlite3

app = Flask(__name__)

# 🔹 Initialize Database
def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coding INTEGER,
            aptitude INTEGER,
            communication INTEGER,
            score REAL
        )
    ''')

    conn.commit()
    conn.close()

# Call database function
init_db()

# 🔹 Home Page
@app.route('/')
def home():
    return render_template('index.html')

# 🔹 Predict + Store Data

@app.route('/predict', methods=['POST'])
def predict():
    coding = int(request.form['coding'])
    aptitude = int(request.form['aptitude'])
    communication = int(request.form['communication'])
    if not (0 <= coding <= 100 and 0 <= aptitude <= 100 and 0 <= communication <= 100):
        return "⚠️ Scores must be between 0 and 100 only!"
    score = (coding + aptitude + communication) / 3
    if score >= 75:
        placement = "High Chance ✅"
    elif score >= 50:
        placement = "Medium Chance ⚠️"
    else:
        placement = "Low Chance ❌"
    weaknesses = []
    recommendations = []
    

   
    if coding < 50:
        weaknesses.append("Coding")
        recommendations.append("Practice DSA problems daily")

    if aptitude < 50:
        weaknesses.append("Aptitude")
        recommendations.append("Practice aptitude questions")

    if communication < 50:
        weaknesses.append("Communication")
        recommendations.append("Practice speaking and mock interviews")

    if not weaknesses:
        weakness_result = "No major weaknesses 🎉"
        recommendation_result = "Keep practicing consistently!"
    else:
        weakness_result = ", ".join(weaknesses)
        recommendation_result = ", ".join(recommendations)
    feedback = ""

    if coding >= 75:
        feedback += "Strong coding skills. "
    else:
        feedback += "Improve coding. "

    if aptitude >= 75:
        feedback += "Good analytical ability. "
    else:
        feedback += "Work on aptitude. "

    if communication >= 75:
        feedback += "Excellent communication. "
    else:
        feedback += "Improve communication. "
    # Store in database
    import sqlite3
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO students (coding, aptitude, communication, score)
        VALUES (?, ?, ?, ?)
    ''', (coding, aptitude, communication, score))

    conn.commit()
    conn.close()

    return render_template(
        'result.html',
        score=score,
        weaknesses=weakness_result,
        recommendations=recommendation_result,
        placement=placement,
        feedback=feedback
    )
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            return redirect('/admin')
        else:
            error = "invalid username or password"

    return render_template('login.html', error=error)
# 🔹 Admin Dashboard
@app.route('/admin')
def admin():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()
    top_student = max(data, key=lambda x: x[4]) if data else None
    return render_template('admin.html', data=data, top_student=top_student)
@app.route('/clear')
def clear():
    import sqlite3
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")

    conn.commit()
    conn.close()

    return redirect('/admin')
@app.route('/generate')
def generate_data():
    import sqlite3
    import random

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    for i in range(100):  # creates 100 students
        coding = random.randint(20, 100)
        aptitude = random.randint(20, 100)
        communication = random.randint(20, 100)

        score = (coding + aptitude + communication) / 3

        cursor.execute('''
            INSERT INTO students (coding, aptitude, communication, score)
            VALUES (?, ?, ?, ?)
        ''', (coding, aptitude, communication, score))

    conn.commit()
    conn.close()

    return render_template('generate.html')
@app.route('/export')
def export():
    import sqlite3
    from openpyxl import Workbook

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title="Student Data"
    # Headers
    ws.append(["ID", "Coding", "Aptitude", "Communication", "Score"])

    # Data
    for row in data:
        ws.append(row)

    file_path = "students.xlsx"
    wb.save(file_path)

    return send_file(file_path, as_attachment=True)
# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)