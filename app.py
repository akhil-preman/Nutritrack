from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from utils.food_db import get_food_nutrition, suggest_foods

app = Flask(__name__)
app.secret_key = 'nutritrack_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutritrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    meals = db.relationship('Meal', backref='user', lazy=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    # New: Tracking Vitamins as required by the abstract
    vit_c = db.Column(db.Float, nullable=False, default=0.0)
    calcium = db.Column(db.Float, nullable=False, default=0.0)
    iron = db.Column(db.Float, nullable=False, default=0.0)
    date_logged = db.Column(db.Date, default=datetime.now)

with app.app_context():
    db.create_all()

def calculate_bmi(weight_kg, height_cm):
    return round(weight_kg / ((height_cm / 100) ** 2), 2)

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif 18.5 <= bmi <= 24.9: return "Normal"
    elif 25 <= bmi <= 29.9: return "Overweight"
    else: return "Obese"

def get_daily_requirements(weight_kg, height_cm, age):
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    req_calories = bmr * 1.2
    
    return {
        "bmr": round(bmr, 1),
        "calories": round(req_calories, 1),
        "protein": round(weight_kg * 0.8, 1),
        "carbs": round((req_calories * 0.5) / 4, 1),
        "fats": round((req_calories * 0.3) / 9, 1),
        "vit_c": 90, # mg
        "calcium": 1000, # mg
        "iron": 18 # mg
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form.get('password'))
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please login.")
            return redirect(url_for('login'))

        new_user = User(
            name=request.form.get('name'), email=email, password_hash=hashed_pw, 
            age=int(request.form.get('age')), height_cm=float(request.form.get('height_cm')), 
            weight_kg=float(request.form.get('weight_kg'))
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    bmi = calculate_bmi(user.weight_kg, user.height_cm)
    reqs = get_daily_requirements(user.weight_kg, user.height_cm, user.age)
    
    # Get date from query param, default to local today
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
        
    todays_meals = Meal.query.filter_by(user_id=user.id, date_logged=selected_date).all()
    
    consumed = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "vit_c": 0, "calcium": 0, "iron": 0}
    for meal in todays_meals:
        consumed["calories"] += meal.calories
        consumed["protein"] += meal.protein
        consumed["carbs"] += meal.carbs
        consumed["fats"] += meal.fats
        consumed["vit_c"] += meal.vit_c
        consumed["calcium"] += meal.calcium
        consumed["iron"] += meal.iron
        
    return render_template('dashboard.html', user=user, bmi=bmi, category=get_bmi_category(bmi),
                           reqs=reqs, consumed=consumed, meals=todays_meals,
                           selected_date=selected_date.strftime('%Y-%m-%d'))

@app.route('/log_meal', methods=['GET', 'POST'])
def log_meal():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
        
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        nutrition = get_food_nutrition(food_name)
        
        if nutrition:
            new_meal = Meal(
                user_id=session['user_id'], food_name=food_name.title(), 
                calories=nutrition['calories'], protein=nutrition['protein'], 
                carbs=nutrition['carbs'], fats=nutrition['fats'],
                vit_c=nutrition['vit_c'], calcium=nutrition['calcium'], iron=nutrition['iron']
            )
            db.session.add(new_meal)
            db.session.commit()
            flash(f"Successfully logged {food_name.title()}!")
            return redirect(url_for('dashboard'))
        flash(f"Sorry, couldn't find '{food_name}'. Try 'Palak Paneer' or 'Chapati'.")
            
    return render_template('log_meal.html', user=user)

@app.route('/weekly')
def weekly():
    if 'user_id' not in session: return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    
    # Get the last 7 days of meals
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6) # 7 days total including today
    
    meals_last_7_days = Meal.query.filter(
        Meal.user_id == user.id,
        Meal.date_logged >= seven_days_ago,
        Meal.date_logged <= today
    ).all()
    
    # Calculate daily requirements and multiply by 7 for the week
    daily_reqs = get_daily_requirements(user.weight_kg, user.height_cm, user.age)
    weekly_reqs = {k: v * 7 for k, v in daily_reqs.items()}
    
    # Sum consumed nutrients over the last 7 days
    consumed = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "vit_c": 0, "calcium": 0, "iron": 0}
    for meal in meals_last_7_days:
        consumed["calories"] += meal.calories
        consumed["protein"] += meal.protein
        consumed["carbs"] += meal.carbs
        consumed["fats"] += meal.fats
        consumed["vit_c"] += meal.vit_c
        consumed["calcium"] += meal.calcium
        consumed["iron"] += meal.iron
        
    # Count how many unique days they logged food
    unique_days = len(set(m.date_logged for m in meals_last_7_days))

    return render_template('weekly.html', user=user, reqs=weekly_reqs, consumed=consumed, days_logged=unique_days)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
