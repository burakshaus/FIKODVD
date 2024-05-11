from flask import Flask, render_template, request, redirect, url_for, session
import pypyodbc as odbc
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database connection details
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP-USG4TN3'
DATABASE_NAME = 'FIKODVD'
username = 'DESKTOP-USG4TN3/Admin'
password = ''

# Connection string with Trusted_Connection=yes for Windows authentication
connection_string = f"DRIVER={{{DRIVER_NAME}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;"

# Use try-except for better error handling
try:
    conn = odbc.connect(connection_string)
except Exception as e:
    print(f"Error connecting to the database: {e}")

@app.route('/')
def home():
    return render_template("Home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM administrators WHERE Username=? AND Passworld=?", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return "Invalid username or password. Please try again."
    return render_template("Login.html")

@app.route('/admin')
def admin():
    if 'username' in session:
        return render_template("Admin.html",username=session['username'])
    return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template("Signup.html")

@app.route('/home')
def backhome():
    return render_template("Home.html")

@app.route('/listdvd')
def listdvd():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds")
    dvds = cursor.fetchall()
    cursor.close()
    return render_template("List.html", dvds=dvds)

@app.route('/add', methods=['GET', 'POST'])
def add_dvd():
    if request.method == 'POST':
        dvdno = request.form['dvdno']
        name = request.form['name']
        country = request.form['country']
        release_year = request.form['shootyear']
        category = request.form['category']
        description = request.form['description']
        casting = request.form['casting']

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dvds VALUES (?, ?, ?, ?, ?, ?, ?)",
            (dvdno, name, country, release_year, category, description, casting))
        conn.commit()
        cursor.close()

        return redirect(url_for('listdvd'))

    return render_template("Adding.html")


if __name__ == '__main__':
    app.run(debug=True)
