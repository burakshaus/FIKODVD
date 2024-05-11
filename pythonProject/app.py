from flask import Flask, render_template, request, redirect, url_for, session
import pypyodbc as odbc

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

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
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password. Please try again."
    return render_template("Login.html")

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome {session['username']}! This is your dashboard."
    return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template("Signup.html")

@app.route('/home')
def backhome():
    return render_template("Home.html")

if __name__ == '__main__':
    app.run(debug=True)
