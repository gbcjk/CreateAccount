from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
from flask_mail import Mail, Message
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gopalbudhathokijk@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'exgi xhqd crni imqn'  # Your Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = 'gopalbudhathokijk@gmail.com'

mail = Mail(app)

def init_db():
    """Initialize the database and create the gopal and password_reset_tokens tables if they don't exist."""
    conn = sqlite3.connect('GBC.db')
    c = conn.cursor()
    
    # Create gopal table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS gopal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # Create password_reset_tokens table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    token TEXT NOT NULL,
                    expiration_time TEXT NOT NULL
                )''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Returns a database connection."""
    conn = sqlite3.connect('GBC.db')
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO gopal (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            conn.commit()
            conn.close()

            # Send welcome email
            send_welcome_email(email)

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose another.', 'danger')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
    return render_template('register.html')

def send_welcome_email(to_email):
    """Sends a welcome email after successful registration."""
    msg = Message('Welcome to Our Service!', recipients=[to_email])
    msg.body = 'Thank you for registering. We are happy to have you on board.'
    try:
        mail.send(msg)
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM gopal WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user:
            if check_password_hash(user['password'], password):
                session['username'] = user['username']
                session['email'] = user['email']  # Store email in session for later use
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}! <br><a href='/logout'>Logout</a>"
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)  # Remove email from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if the email exists in the database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM gopal WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user:
            # Generate a reset token (simulated here with expiration)
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            expiration_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour
            
            # Store token and expiration (for the sake of the example)
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO password_reset_tokens (email, token, expiration_time) VALUES (?, ?, ?)", 
                      (email, reset_token, expiration_time))
            conn.commit()
            conn.close()

            # Send email with the reset link
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            send_reset_email(email, reset_link)

            flash(f'A password reset link has been sent to {email}.', 'info')
            return redirect(url_for('login'))
        else:
            flash('No account found with this email address.', 'danger')

    return render_template('forgot_password.html')

def send_reset_email(to_email, reset_link):
    """Sends a password reset email."""
    msg = Message('Password Reset Request', recipients=[to_email])
    msg.body = f'Click the link below to reset your password:\n{reset_link}'
    try:
        mail.send(msg)
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        # Hash new password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        # Check if token exists and is valid (expired check here)
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM password_reset_tokens WHERE token = ?", (token,))
        reset_token = c.fetchone()

        if reset_token:
            # Adjust the format to handle milliseconds (if present)
            try:
                expiration_time = datetime.strptime(reset_token['expiration_time'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                expiration_time = datetime.strptime(reset_token['expiration_time'], '%Y-%m-%d %H:%M:%S.%f')

            if datetime.now() < expiration_time:
                # Valid token, reset password
                c.execute("UPDATE gopal SET password = ? WHERE email = ?", (hashed_password, reset_token['email']))
                conn.commit()
                flash('Your password has been reset successfully.', 'success')
                return redirect(url_for('login'))
            else:
                flash('This reset token has expired.', 'danger')
        else:
            flash('Invalid reset token.', 'danger')

        conn.close()

    return render_template('reset_password.html', token=token)


if __name__ == '__main__':
    init_db()  # Initializes the database and creates the tables if they don't exist
    app.run(debug=True)
