from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# A secret key is needed to keep the client-side sessions secure. 
# In a real app, this should be a random, hard-to-guess string.
app.secret_key = 'nutritrack_secret_key'

# Configure SQLite Database. It will be created in the 'instance' folder.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutritrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)

# Create database tables within the application context
with app.app_context():
    db.create_all()

def calculate_bmi(weight_kg, height_cm):
    # BMI Formula: weight in kg divided by height in meters squared
    # Since height is in cm, we divide by 100 to get meters (height_cm / 100)
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi <= 24.9:
        return "Normal"
    elif 25 <= bmi <= 29.9:
        return "Overweight"
    else:
        return "Obese"

@app.route('/')
def home():
    # Render the simple home page
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = int(request.form.get('age'))
        height_cm = float(request.form.get('height_cm'))
        weight_kg = float(request.form.get('weight_kg'))

        # Hash the password for security
        hashed_pw = generate_password_hash(password)

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please login.")
            return redirect(url_for('login'))

        # Create new user and save to DB
        new_user = User(name=name, email=email, password_hash=hashed_pw, 
                        age=age, height_cm=height_cm, weight_kg=weight_kg)
        db.session.add(new_user)
        db.session.commit()

        # Calculate BMI and save user info in session
        bmi = calculate_bmi(weight_kg, height_cm)
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_age'] = new_user.age
        session['bmi'] = bmi
        
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # Check if user exists and password hash matches
        if user and check_password_hash(user.password_hash, password):
            # Login successful, setup session
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_age'] = user.age
            session['bmi'] = calculate_bmi(user.weight_kg, user.height_cm)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Protect route: check if user is logged in
    if 'user_id' not in session:
        flash("Please log in to view the dashboard.")
        return redirect(url_for('login'))
        
    bmi = session.get('bmi')
    category = get_bmi_category(bmi)
    
    return render_template('dashboard.html', 
                           name=session.get('user_name'), 
                           age=session.get('user_age'), 
                           bmi=bmi, 
                           category=category)

@app.route('/logout')
def logout():
    session.clear() # Clear all data stored in the session
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
