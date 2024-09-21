from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

# Define the base directory where user folders will be stored
BASE_SFTP_DIR = 'sftp_users'

# Function to create a new session
def create_session(user_id):
    session_id = str(uuid4())  # Generate a unique session ID
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO sessions (session_id, user_id) VALUES (%s, %s)", (session_id, user_id))
    mysql.connection.commit()
    return session_id

# Function to create a new session
#def create_session(user_id):
#    session_id = str(uuid4())  # Generate a unique session ID
#    cur = mysql.connection.cursor()
#    cur.execute("INSERT INTO sessions (session_id, user_id) VALUES (%s, %s)", (session_id, user_id))
#    mysql.connection.commit()
#    return session_id

# Function to create an SFTP folder for a user
def create_user_sftp_folder(email, phone):
    folder_name = email + phone  # Folder name as email + phone
    folder_path = os.path.join(BASE_SFTP_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't already exist
    return folder_path

# Function to save user folder path in the database
def save_user_folder(user_id, folder_path):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user_folders (user_id, folder_path) VALUES (%s, %s)", (user_id, folder_path))
    mysql.connection.commit()

# Route for login
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    
    if user and check_password_hash(user[4], password):
        session_id = create_session(user[0])  # Create a session and get the session ID
        return redirect(url_for('dashboard', session_id=session_id))
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

# Route for registering a user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, password))
        mysql.connection.commit()
        
        # Get the newly created user ID
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user_id = cur.fetchone()[0]
        
        # Create SFTP folder for the user
        folder_path = create_user_sftp_folder(email, phone)
        
        # Save the folder path in the database
        save_user_folder(user_id, folder_path)
        
        return redirect(url_for('index'))
    return render_template('register.html')

# Function to get the images in the user's SFTP folder
def get_images_from_folder(folder_path):
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    images = []
    for file_name in os.listdir(folder_path):
        if file_name.split('.')[-1].lower() in allowed_extensions:
            images.append(file_name)
    return images

# Route for profile (session protected)
@app.route('/profile')
def profile():
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid session')
        return redirect(url_for('index'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sessions WHERE session_id=%s AND active=TRUE", (session_id,))
    session_data = cur.fetchone()
    
    if not session_data:
        flash('Session has expired or is invalid')
        return redirect(url_for('index'))
    
    user_id = session_data[2]
    
    # Fetch user details
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    # Fetch user's folder path
    cur.execute("SELECT folder_path FROM user_folders WHERE user_id=%s", (user_id,))
    folder_path = cur.fetchone()[0]
    
    # Get images from user's folder
    images = get_images_from_folder(folder_path)
    
    return render_template('profile.html', user=user, images=images, folder_path=folder_path)

# Route for dashboard (session protected)
@app.route('/dashboard')
def dashboard():
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid session')
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', session_id=session_id)

# Route for logout
@app.route('/logout')
def logout():
    session_id = request.args.get('session_id')
    
    if session_id:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE sessions SET active=FALSE, end_time=%s WHERE session_id=%s",
                    (datetime.now(), session_id))
        mysql.connection.commit()
        flash('You have been logged out')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(BASE_SFTP_DIR):
        os.makedirs(BASE_SFTP_DIR)
    app.run(debug=True)
