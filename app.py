# Store this code in 'app.py'
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'abivini@123'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abisha@123'
app.config['MYSQL_DB'] = 'geekprofile1'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    account = None  # Ensuring the variable is initialized

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()
        
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        required_fields = ['username', 'password', 'email', 'address', 'city', 'country', 'postalcode', 'organisation']
        if all(field in request.form for field in required_fields):
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            organisation = request.form['organisation']
            address = request.form['address']
            city = request.form['city']
            state = request.form.get('state', '')  # Use `.get()` to avoid KeyError if 'state' is missing
            country = request.form['country']
            postalcode = request.form['postalcode']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                cursor.execute(
                    'INSERT INTO accounts (username, password, email, organisation, address, city, state, country, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (username, password, email, organisation, address, city, state, country, postalcode)
                )
                mysql.connection.commit()
                cursor.close()
                msg = 'You have successfully registered!'
        else:
            msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/display')
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        return render_template('display.html', account=account)
    return redirect(url_for('login'))

@app.route('/update', methods=['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            required_fields = ['username', 'password', 'email', 'address', 'city', 'country', 'postalcode', 'organisation']
            if all(field in request.form for field in required_fields):
                username = request.form['username']
                password = request.form['password']
                email = request.form['email']
                organisation = request.form['organisation']
                address = request.form['address']
                city = request.form['city']
                state = request.form.get('state', '')  # Use `.get()` to avoid KeyError if 'state' is missing
                country = request.form['country']
                postalcode = request.form['postalcode']

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
                account = cursor.fetchone()

                if account and account['id'] != session['id']:
                    msg = 'Username already taken by another user!'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address!'
                elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'Username must contain only characters and numbers!'
                else:
                    cursor.execute(
                        'UPDATE accounts SET username=%s, password=%s, email=%s, organisation=%s, address=%s, city=%s, state=%s, country=%s, postalcode=%s WHERE id=%s',
                        (username, password, email, organisation, address, city, state, country, postalcode, session['id'])
                    )
                    mysql.connection.commit()
                    cursor.close()
                    msg = 'Profile updated successfully!'
            else:
                msg = 'Please fill out the form!'

        return render_template('update.html', msg=msg)

    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
