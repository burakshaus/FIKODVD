from flask import Flask, render_template, request, redirect, url_for, session, flash
import pypyodbc as odbc
import secrets
import bcrypt
from datetime import datetime, date
from time import sleep

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

def initialize_daily_rental_count():
    today = date.today()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM daily_rental_count WHERE rental_date = ?", (today,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO daily_rental_count (rental_date, rental_count) VALUES (?, 0)", (today,))
            conn.commit()
    except Exception as e:
        print(f"Error initializing daily rental count: {e}")
    finally:
        cursor.close()


@app.route('/home')
@app.route('/')
def home():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds ORDER BY rental_count DESC")
    dvds = cursor.fetchall()
    cursor.close()
    initialize_daily_rental_count()
    return render_template("Home.html", dvds=dvds)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Passworld FROM administrators WHERE Username=?", (username,))
            stored_hash = cursor.fetchone()
            if stored_hash:
                stored_hash = stored_hash[0]
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    session['username'] = username
                    return redirect(url_for('admin'))
                else:
                    flash("Invalid username or password. Please try again.")
            else:
                flash("User not found. Please try again.")
        except Exception as e:
            flash(f"An error occurred: {e}")

    # Render the template with flashed messages
    return render_template("Login.html")

@app.route('/admin')
def admin():
    if 'username' in session:
        return render_template("Admin.html",username=session['username'])
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        tcno = request.form['tcno']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO administrators (TCno, Username, Passworld) VALUES (?, ?, ?)",
                           (tcno, username, hashed_password))
            conn.commit()
            cursor.close()
            return redirect(url_for('login'))
        except Exception as e:
            return f"An error occurred: {e}"

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
        name = request.form['name']
        country = request.form['country']
        release_year = request.form['shootyear']
        category = request.form['category']
        description = request.form['description']
        casting = request.form['casting']
        image = request.form['image']
        stock = request.form['stock']
        rental_count = 0

        try:
            stock = int(stock)  # Convert stock to integer
            if stock < 0 or stock > 2:
                raise ValueError("Stock must be between 0 and 2.")
        except ValueError as e:
            return f"Error: {e}"

        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO dvds (dvdname, country, shootyear, catagory, dvddescription, casting, img, stock,rental_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)",
                (name, country, release_year, category, description, casting, image, stock,rental_count))
            conn.commit()
            cursor.close()

            return redirect(url_for('listdvd'))
        except Exception as e:
            return f"An error occurred: {e}"

    return render_template("Adding.html")

@app.route('/deletedvd', methods=['POST'])
def delete_dvd():
    if request.method == 'POST':
        dvd_id = request.form['dvd_id']

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dvds WHERE id=?", (dvd_id,))
            conn.commit()
            cursor.close()
            return redirect(url_for('listdvd'))
        except Exception as e:
            return f"An error occurred: {e}"

    return redirect(url_for('listdvd'))  # Redirect to the DVDs page


@app.route('/edit/<int:dvd_id>', methods=['GET', 'POST'])
def edit(dvd_id):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds WHERE id=?", (dvd_id,))
    dvd = cursor.fetchone()
    cursor.close()

    return render_template("Edit.html", dvd=dvd)


@app.route('/edit_dvd', methods=['GET', 'POST'])
def edit_dvd():
    if request.method == 'POST':
        dvd_id = request.form['dvd_id']
        name = request.form['name']
        country = request.form['country']
        release_year = request.form['shootyear']
        category = request.form['category']
        description = request.form['description']
        casting = request.form['casting']
        image = request.form['image']
        stock = request.form['stock']
        rental_count = request.form['rental']


        try:
            stock = int(stock)  # Convert stock to integer
            if stock < 0 or stock > 2:
                raise ValueError("Stock must be between 0 and 2.")
        except ValueError as e:
            return f"Error: {e}"

        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE dvds SET dvdname=?, country=?, shootyear=?, catagory=?, dvddescription=?, casting=?, img=?, stock=?, rental_count=? WHERE id=?",
                (name, country, release_year, category, description, casting, image, stock, rental_count, dvd_id))
            conn.commit()
            cursor.close()

            return redirect(url_for('listdvd'))
        except Exception as e:
            return f"An error occurred: {e}"

    # Fetch the DVD data to pre-populate the form
    dvd_id = request.args.get('dvd_id')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds WHERE id=?", (dvd_id,))
    dvd = cursor.fetchone()
    cursor.close()

    return render_template("edit.html", dvd=dvd)


@app.route('/listall')
def listall():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds")
    dvds = cursor.fetchall()
    cursor.close()
    return render_template("listdvd.html", dvds=dvds)


@app.route('/buy/<int:dvd_id>')
def buy_dvd(dvd_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvds WHERE Id=?", (dvd_id,))
    dvd = cursor.fetchone()
    cursor.close()
    return render_template("buy.html", dvd=dvd)


@app.route('/rent/<int:dvd_id>', methods=['GET', 'POST'])
def rent_dvd(dvd_id):
    if request.method == 'POST':
        tcno = request.form['tcno']
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        rent_date = request.form['rent_date']
        return_date = request.form['return_date']
        rent_days = int(request.form['rent_days'])

        # Calculate rental fee
        rental_fee = rent_days * 25  # Assuming 25 TL per day

        # Calculate late fee if the DVD is returned after the due date
        return_date = datetime.strptime(return_date, "%Y-%m-%d")
        today = datetime.now()
        days_overdue = (today - return_date).days
        late_fee = max(0, days_overdue) * 10  # Late fee is 10 TL per day, capped at 0

        # Total fee is the sum of rental fee and late fee
        total_fee = rental_fee + late_fee

        # Check if the client already exists in the clients table
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM clients WHERE Tcno=?", (tcno,))
        existing_client = cursor.fetchone()

        if existing_client is None:
            # Insert the new client into the clients table
            cursor.execute("INSERT INTO clients (Tcno, Firstname, Lastname, Telno) VALUES (?, ?, ?, ?)",
                           (tcno, name, surname, phone))
            conn.commit()

            # Retrieve the new client_id
            cursor.execute("SELECT Id FROM clients WHERE Tcno=?", (tcno,))
            client_id = cursor.fetchone()[0]
        else:
            # Use the existing client_id
            client_id = existing_client[0]

        # Fetch the DVD's stock from the database
        cursor.execute("SELECT stock FROM dvds WHERE Id=?", (dvd_id,))
        current_stock = cursor.fetchone()[0]

        if current_stock > 0:
            # Decrement the stock by 1
            new_stock = current_stock - 1

            # Update the stock in the database
            cursor.execute("UPDATE dvds SET stock=? WHERE Id=?", (new_stock, dvd_id))
            conn.commit()

            # Insert the rental information into the dvd_rentals table
            cursor.execute("INSERT INTO dvd_rentals (dvd_id, rent_date, return_date, rental_fee, late_fee, total_fee, client_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (dvd_id, rent_date, return_date, rental_fee, late_fee, total_fee, client_id))
            conn.commit()

            cursor.execute("UPDATE dvds SET rental_count=rental_count+1 WHERE Id=?", (dvd_id,))
            conn.commit()

            cursor.close()

            # Update the daily rental count
            rental_date = date.today()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT rental_count FROM daily_rental_count WHERE rental_date=?", (rental_date,))
                rental_count = cursor.fetchone()
                if rental_count is None:
                    # No entry for this date, insert a new row
                    cursor.execute("INSERT INTO daily_rental_count (rental_date, rental_count) VALUES (?, 1)",
                                   (rental_date,))
                else:
                    # Update the existing row
                    cursor.execute("UPDATE daily_rental_count SET rental_count = rental_count + 1 WHERE rental_date=?",
                                   (rental_date,))
                conn.commit()
            except Exception as e:
                return f"An error occurred: {e}"
            finally:
                cursor.close()

            return redirect(url_for('home'))
        else:
            flash("This DVD is out of stock.")

    return render_template("buy.html", dvd_id=dvd_id)

@app.route('/list_dvd_rentals')
def list_dvd_rentals():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dvd_rentals")
    dvd_rentals = cursor.fetchall()
    cursor.close()
    return render_template("Rentals.html", dvd_rentals=dvd_rentals)

@app.route('/list_clients')
def list_clients():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    cursor.close()
    return render_template("Clients.html", clients=clients)

@app.route('/deleterental', methods=['POST'])
def deleterental():
    if request.method == 'POST':
        rental_id = request.form['rental_id']

        cursor = conn.cursor()
        try:
            # Fetch the DVD ID of the rental being deleted
            cursor.execute("SELECT dvd_id FROM dvd_rentals WHERE rental_id=?", (rental_id,))
            dvd_id = cursor.fetchone()[0]

            # Delete the rental from the dvd_rentals table
            cursor.execute("DELETE FROM dvd_rentals WHERE rental_id=?", (rental_id,))
            conn.commit()

            # Increment the stock of the corresponding DVD by 1
            cursor.execute("UPDATE dvds SET stock = stock + 1 WHERE Id=?", (dvd_id,))
            conn.commit()

            cursor.close()
            return redirect(url_for('list_dvd_rentals'))
        except Exception as e:
            return f"An error occurred: {e}"

    return redirect(url_for('list_dvd_rentals'))  # Redirect to the rentals page

def calculate_late_fee(old_return_date, new_return_date):
    # Calculate the difference in days between the new and old return dates
    new_return_date = datetime.strptime(new_return_date, "%Y-%m-%d")
    old_return_date = datetime.strptime(old_return_date, "%Y-%m-%d")
    days_overdue = (new_return_date - old_return_date).days
    # Late fee is 10 TL per day, capped at 0
    late_fee = max(0, days_overdue) * 10
    return late_fee

@app.route('/adjustrental', methods=['GET', 'POST'])
def adjustrental():
    if request.method == 'POST':
        rental_id = request.form['rental_id']
        rent_date = request.form['rent_date']
        return_date = request.form['return_date']
        rental_fee = float(request.form['rental_fee'])  # Convert to float

        # Fetch the old return date from the database
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT return_date FROM dvd_rentals WHERE rental_id=?", (rental_id,))
            old_return_date = cursor.fetchone()[0]
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            cursor.close()

        # Calculate the late fee between the old and new returning dates
        late_fee = calculate_late_fee(old_return_date, return_date)

        # Calculate the total fee
        total_fee = rental_fee + late_fee  # Update total fee to include late fee

        # Update the rental information in the database
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE dvd_rentals SET rent_date=?, return_date=?, rental_fee=?, late_fee=?, total_fee=? WHERE rental_id=?",
                (rent_date, return_date, rental_fee, late_fee, total_fee, rental_id))
            conn.commit()
            return redirect(url_for('list_dvd_rentals'))
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            cursor.close()

    else:
        rental_id = request.args.get('rental_id')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM dvd_rentals WHERE rental_id=?", (rental_id,))
            rental = cursor.fetchone()
            if rental:
                return render_template("Adjust.html", rental=rental)
            else:
                return "Rental not found."
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            cursor.close()

    return redirect(url_for('list_dvd_rentals'))

@app.route('/analysis')
def analysis():
    cursor = conn.cursor()
    cursor.execute("SELECT rental_date, rental_count FROM daily_rental_count ORDER BY rental_date")
    rows = cursor.fetchall()
    return render_template('analysis.html', rental_counts=rows)

@app.route('/inforental/<int:rental_id>')
def inforental(rental_id):
    try:
        cursor = conn.cursor()

        # Fetch rental details
        cursor.execute("SELECT * FROM dvd_rentals WHERE rental_id=?", (rental_id,))
        rental = cursor.fetchone()

        if not rental:
            raise Exception("Rental not found.")

        # Fetch DVD details
        cursor.execute("SELECT * FROM dvds WHERE id=?", (rental[1],))  # Assuming DVD ID is in rental[1]
        dvd = cursor.fetchone()

        if not dvd:
            raise Exception("DVD not found.")

        # Fetch client details
        cursor.execute("SELECT * FROM clients WHERE Id=?", (rental[7],))  # Assuming Client ID is in rental[7]
        client = cursor.fetchone()

        if not client:
            raise Exception("Client not found.")

        cursor.close()

        return render_template("Rentalinfo.html", rental=rental, dvd=dvd, client=client)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/deleteclient', methods=['GET', 'POST'])
def deleteclient():
    if request.method == 'POST':
        client_id = request.form['client_id']

        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
                conn.commit()
            return redirect(url_for('list_clients'))
        except Exception as e:
            return f"An error occurred: {e}"

    return redirect(url_for('list_clients'))  # Redirect to the clients page



if __name__ == '__main__':
    app.run(debug=True)
