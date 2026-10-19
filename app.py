from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.food_db import get_food_nutrition, suggest_foods, search_food_names, add_custom_food, delete_custom_food, get_all_foods, is_count_based_food, FOOD_DATA
from utils.ai_engine import predict_food_from_image, generate_weekly_deficiencies
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nutritrack_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutritrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    goal = db.Column(db.String(20), default='maintain')
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

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()
    # Ensure default admin account exists
    default_admin = Admin.query.filter_by(username='admin').first()
    if not default_admin:
        default_admin = Admin(
            username='admin',
            email='admin@nutritrack.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(default_admin)
        db.session.commit()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Please sign in as an administrator to access the Admin Portal.")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_bmi(weight_kg, height_cm):
    return round(weight_kg / ((height_cm / 100) ** 2), 2)

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif 18.5 <= bmi <= 24.9: return "Normal"
    elif 25 <= bmi <= 29.9: return "Overweight"
    else: return "Obese"

def get_daily_requirements(weight_kg, height_cm, age, goal="maintain"):
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    maint_calories = bmr * 1.2
    
    if goal == "cut":
        req_calories = maint_calories - 500
        protein = weight_kg * 1.6 # Higher protein when cutting
    elif goal == "gain":
        req_calories = maint_calories + 500
        protein = weight_kg * 1.2 # slightly higher protein
    else:
        req_calories = maint_calories
        protein = weight_kg * 0.8
        
    return {
        "bmr": round(bmr, 1),
        "calories": round(req_calories, 1),
        "protein": round(protein, 1),
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
            weight_kg=float(request.form.get('weight_kg')), goal=request.form.get('goal', 'maintain')
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
    reqs = get_daily_requirements(user.weight_kg, user.height_cm, user.age, user.goal)
    
    today = datetime.now().date()
    
    # Get date from query param, default to local today
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
        
    is_today = (selected_date == today)
        
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
                           selected_date=selected_date.strftime('%Y-%m-%d'), 
                           is_today=is_today, datetime_now=today.strftime('%Y-%m-%d'))

@app.route('/log_meal', methods=['GET', 'POST'])
def log_meal():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    found_food = None
    query_param = request.args.get('food', '').strip()
        
    if request.method == 'POST':
        food_name = request.form.get('food_name')
        nutrition = get_food_nutrition(food_name)
        
        if nutrition:
            # Instead of saving, just return the data to the template to show the modal
            found_food = {
                "name": food_name.title(),
                "nutrition": nutrition,
                "is_count_based": is_count_based_food(food_name)
            }
        else:
            flash(f"Sorry, couldn't find '{food_name}'. Try 'Palak Paneer' or 'Egg'.")
    elif query_param:
        nutrition = get_food_nutrition(query_param)
        if not nutrition:
            # Try finding closest match in DB
            matches = search_food_names(query_param, limit=1)
            if not matches:
                for word in query_param.split():
                    if len(word) >= 3 and word.lower() not in ['with', 'and', 'the', 'for', 'curry', 'fresh', 'milk', 'pure']:
                        matches = search_food_names(word, limit=1)
                        if matches: break
            if matches:
                nutrition = get_food_nutrition(matches[0])
                if nutrition:
                    query_param = matches[0]

        if nutrition:
            found_food = {
                "name": query_param.title(),
                "nutrition": nutrition,
                "is_count_based": is_count_based_food(query_param)
            }
            
    return render_template('log_meal.html', user=user, found_food=found_food, initial_query=query_param)

@app.route('/confirm_log_meal', methods=['POST'])
def confirm_log_meal():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    food_name = request.form.get('food_name', '')
    is_count = request.form.get('is_count_based') == '1' or is_count_based_food(food_name)
    
    if is_count:
        num = float(request.form.get('quantity_num') or request.form.get('quantity', 1))
        if num < 1: num = 1
        factor = num
        portion_label = f"{int(num) if num.is_integer() else num}x"
    else:
        grams = float(request.form.get('grams') or request.form.get('quantity', 100))
        if grams < 1: grams = 1
        factor = grams / 100.0
        portion_label = f"{int(grams) if grams.is_integer() else grams}g"
            
    nutrition = get_food_nutrition(food_name)
    
    if nutrition:
        new_meal = Meal(
            user_id=session['user_id'], 
            food_name=f"{portion_label} {food_name.title()}", 
            calories=round(nutrition['calories'] * factor, 1), 
            protein=round(nutrition['protein'] * factor, 1), 
            carbs=round(nutrition['carbs'] * factor, 1), 
            fats=round(nutrition['fats'] * factor, 1),
            vit_c=round(nutrition['vit_c'] * factor, 1), 
            calcium=round(nutrition['calcium'] * factor, 1), 
            iron=round(nutrition['iron'] * factor, 1)
        )
        db.session.add(new_meal)
        db.session.commit()
        flash(f"Successfully logged {portion_label} of {food_name.title()}!")
        return redirect(url_for('dashboard'))
        
    flash("Error logging meal.")
    return redirect(url_for('log_meal'))

@app.route('/predict_meal', methods=['POST'])
def predict_meal():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    if 'food_image' not in request.files:
        flash("No file part")
        return redirect(url_for('log_meal'))
        
    file = request.files['food_image']
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('log_meal'))
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run AI prediction via OpenCV + MobileNet pipeline
        predicted_food = predict_food_from_image(filepath)
        
        # Cleanup uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
            
        if predicted_food == "error_missing_api_key":
            flash("AI Engine Error: GEMINI_API_KEY is missing in your .env file!")
            return redirect(url_for('log_meal'))
        elif predicted_food == "error_api_failed":
            flash("AI Engine Error: Failed to connect to Gemini API. Check your internet or API key.")
            return redirect(url_for('log_meal'))
        elif predicted_food == "error_invalid_image":
            flash("AI Engine Error: Invalid image uploaded.")
            return redirect(url_for('log_meal'))
            
        nutrition = get_food_nutrition(predicted_food)
        if nutrition:
            # Trigger confirmation modal instead of instant save
            found_food = {
                "name": predicted_food.title(),
                "nutrition": nutrition,
                "is_ai": True,
                "is_count_based": is_count_based_food(predicted_food)
            }
            return render_template('log_meal.html', user=user, found_food=found_food)
            
        flash(f"AI predicted '{predicted_food}', but it's not in our database.")
        return redirect(url_for('log_meal'))

@app.route('/weekly')
def weekly():
    if 'user_id' not in session: return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    
    today = datetime.now().date()
    cur_monday = today - timedelta(days=today.weekday())
    last_completed_monday = cur_monday - timedelta(days=7)
    
    # 1. Determine selected week from query param
    week_str = request.args.get('week') or request.args.get('date')
    if week_str:
        try:
            target_date = datetime.strptime(week_str.split('_')[0], '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=target_date.weekday())
        except ValueError:
            start_date = last_completed_monday
    else:
        # Default: if current week has logged meals, default to current week; otherwise default to last completed week
        cur_sunday = cur_monday + timedelta(days=6)
        cur_count = Meal.query.filter(Meal.user_id == user.id, Meal.date_logged >= cur_monday, Meal.date_logged <= cur_sunday).count()
        start_date = cur_monday if cur_count > 0 else last_completed_monday
        
    end_date = start_date + timedelta(days=6)
    
    # 2. Build 7-day date grouped weeks list for selector (going back to earliest meal or 10 weeks)
    earliest_date = today - timedelta(days=70)
    earliest_meal = Meal.query.filter_by(user_id=user.id).order_by(Meal.date_logged.asc()).first()
    if earliest_meal and earliest_meal.date_logged:
        earliest_date = min(earliest_date, earliest_meal.date_logged)
    earliest_monday = earliest_date - timedelta(days=earliest_date.weekday())
    
    available_weeks = []
    mon = cur_monday
    while mon >= earliest_monday:
        sun = mon + timedelta(days=6)
        is_cur = (mon == cur_monday)
        is_last = (mon == last_completed_monday)
        
        dates_label = f"{mon.strftime('%d %b %Y')} – {sun.strftime('%d %b %Y')}"
        if is_cur:
            label = f"{dates_label} (Current Week)"
        elif is_last:
            label = f"{dates_label} (Completed Week)"
        else:
            label = dates_label
            
        available_weeks.append({
            "start": mon.strftime('%Y-%m-%d'),
            "end": sun.strftime('%Y-%m-%d'),
            "label": label,
            "is_current": is_cur,
            "is_completed": is_last
        })
        mon -= timedelta(days=7)
        
    prev_week_start = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
    next_monday = start_date + timedelta(days=7)
    next_week_start = next_monday.strftime('%Y-%m-%d') if next_monday <= cur_monday else None
    
    # 3. Query meals for the selected 7-day week
    meals_for_week = Meal.query.filter(
        Meal.user_id == user.id,
        Meal.date_logged >= start_date,
        Meal.date_logged <= end_date
    ).all()
    
    daily_reqs = get_daily_requirements(user.weight_kg, user.height_cm, user.age, user.goal)
    weekly_reqs = {k: v * 7 for k, v in daily_reqs.items()}
    
    consumed = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "vit_c": 0, "calcium": 0, "iron": 0}
    for meal in meals_for_week:
        consumed["calories"] += meal.calories
        consumed["protein"] += meal.protein
        consumed["carbs"] += meal.carbs
        consumed["fats"] += meal.fats
        consumed["vit_c"] += meal.vit_c
        consumed["calcium"] += meal.calcium
        consumed["iron"] += meal.iron
        
    unique_days = len(set(m.date_logged for m in meals_for_week))
    week_label = f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"
    
    return render_template(
        'weekly.html', 
        user=user, 
        reqs=weekly_reqs, 
        daily_reqs=daily_reqs, 
        consumed=consumed, 
        days_logged=unique_days,
        available_weeks=available_weeks,
        selected_week_start=start_date.strftime('%Y-%m-%d'),
        selected_week_end=end_date.strftime('%Y-%m-%d'),
        week_label=week_label,
        prev_week_start=prev_week_start,
        next_week_start=next_week_start,
        is_current_week=(start_date == cur_monday),
        is_completed_week=(end_date < today)
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            user.age = int(request.form.get('age'))
            user.height_cm = float(request.form.get('height_cm'))
            user.weight_kg = float(request.form.get('weight_kg'))
            if request.form.get('goal'):
                user.goal = request.form.get('goal')
            db.session.commit()
            flash('Profile updated successfully! New goals calculated.')
        except ValueError:
            flash('Invalid input. Please enter valid numbers.')
            
        return redirect(url_for('profile'))
        
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/api/suggestions')
def api_suggestions():
    query = request.args.get('q', '')
    suggestions = search_food_names(query)
    return jsonify(suggestions)


@app.route('/api/generate_weekly_insights')
def api_generate_weekly_insights():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(session['user_id'])
    
    today = datetime.now().date()
    cur_monday = today - timedelta(days=today.weekday())
    last_completed_monday = cur_monday - timedelta(days=7)
    
    week_str = request.args.get('week') or request.args.get('start') or request.args.get('date')
    if week_str:
        try:
            target_date = datetime.strptime(week_str.split('_')[0], '%Y-%m-%d').date()
            start_date = target_date - timedelta(days=target_date.weekday())
        except ValueError:
            start_date = last_completed_monday
    else:
        cur_sunday = cur_monday + timedelta(days=6)
        cur_count = Meal.query.filter(Meal.user_id == user.id, Meal.date_logged >= cur_monday, Meal.date_logged <= cur_sunday).count()
        start_date = cur_monday if cur_count > 0 else last_completed_monday
        
    end_date = start_date + timedelta(days=6)
    
    meals = Meal.query.filter(
        Meal.user_id == user.id, 
        Meal.date_logged >= start_date, 
        Meal.date_logged <= end_date
    ).all()
    
    unique_days = len(set(m.date_logged for m in meals))
    if unique_days == 0:
        return jsonify([])
        
    daily_reqs = get_daily_requirements(user.weight_kg, user.height_cm, user.age, user.goal)
    weekly_reqs = {k: v * 7 for k, v in daily_reqs.items()}
    
    consumed = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "vit_c": 0, "calcium": 0, "iron": 0}
    for meal in meals:
        consumed["calories"] += meal.calories
        consumed["protein"] += meal.protein
        consumed["carbs"] += meal.carbs
        consumed["fats"] += meal.fats
        consumed["vit_c"] += meal.vit_c
        consumed["calcium"] += meal.calcium
        consumed["iron"] += meal.iron
        
    deficiencies = generate_weekly_deficiencies(consumed, weekly_reqs, unique_days)
    return jsonify(deficiencies)


# ==========================================
# ADMIN MODULE ROUTES
# ==========================================

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_meals = Meal.query.count()
    total_calories = db.session.query(db.func.sum(Meal.calories)).scalar() or 0.0
    total_foods = len(FOOD_DATA)
    
    goal_cut = User.query.filter_by(goal='cut').count()
    goal_maintain = User.query.filter_by(goal='maintain').count()
    goal_gain = User.query.filter_by(goal='gain').count()
    
    recent_users_raw = User.query.order_by(User.id.desc()).limit(5).all()
    recent_users = []
    for u in recent_users_raw:
        bmi = calculate_bmi(u.weight_kg, u.height_cm)
        recent_users.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "goal": u.goal or 'maintain',
            "bmi": bmi,
            "bmi_category": get_bmi_category(bmi),
            "meals_count": len(u.meals)
        })
        
    today = datetime.now().date()
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
        
    is_today = (selected_date == today)
        
    recent_meals_raw = Meal.query.filter(Meal.date_logged == selected_date).order_by(Meal.id.desc()).all()
    recent_meals = []
    for m in recent_meals_raw:
        recent_meals.append({
            "id": m.id,
            "user_name": m.user.name if m.user else "Unknown User",
            "food_name": m.food_name,
            "calories": m.calories,
            "protein": m.protein,
            "carbs": m.carbs,
            "fats": m.fats,
            "date_logged": m.date_logged.strftime('%Y-%m-%d') if m.date_logged else ""
        })
        
    stats = {
        "total_users": total_users,
        "total_meals": total_meals,
        "total_calories": total_calories,
        "total_foods": total_foods,
        "goal_cut": goal_cut,
        "goal_maintain": goal_maintain,
        "goal_gain": goal_gain
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_meals=recent_meals,
                           selected_date=selected_date.strftime('%Y-%m-%d'),
                           is_today=is_today,
                           datetime_now=today.strftime('%Y-%m-%d'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        login_input = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = Admin.query.filter((Admin.username == login_input) | (Admin.email == login_input)).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            session['admin_email'] = admin.email
            flash(f"Welcome back, {admin.username}!", "success")
            return redirect(url_for('admin_dashboard'))
            
        flash("Invalid admin username or password.")
        
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_email', None)
    flash("You have been logged out of the Admin Portal.")
    return redirect(url_for('admin_login'))

@app.route('/admin/users')
@admin_required
def admin_users():
    q = request.args.get('q', '').strip()
    selected_goal = request.args.get('goal', '').strip()
    
    query = User.query
    if q:
        query = query.filter((User.name.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%')))
    if selected_goal:
        query = query.filter_by(goal=selected_goal)
        
    users_raw = query.order_by(User.id.desc()).all()
    users = []
    for u in users_raw:
        bmi = calculate_bmi(u.weight_kg, u.height_cm)
        users.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "age": u.age,
            "height_cm": u.height_cm,
            "weight_kg": u.weight_kg,
            "goal": u.goal or 'maintain',
            "bmi": bmi,
            "bmi_category": get_bmi_category(bmi),
            "meals_count": len(u.meals)
        })
        
    return render_template('admin/users.html', users=users, query=q, selected_goal=selected_goal)

@app.route('/admin/user/<int:user_id>/meals')
@admin_required
def admin_user_meals(user_id):
    target_user = User.query.get_or_404(user_id)
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date_logged.desc(), Meal.id.desc()).all()
    bmi = calculate_bmi(target_user.weight_kg, target_user.height_cm)
    bmi_category = get_bmi_category(bmi)
    reqs = get_daily_requirements(target_user.weight_kg, target_user.height_cm, target_user.age, target_user.goal)
    
    return render_template('admin/user_meals.html', target_user=target_user, meals=meals, bmi=bmi, bmi_category=bmi_category, reqs=reqs)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    target_user = User.query.get_or_404(user_id)
    user_name = target_user.name
    Meal.query.filter_by(user_id=user_id).delete()
    db.session.delete(target_user)
    db.session.commit()
    flash(f"User '{user_name}' and their logged meals have been deleted successfully.")
    return redirect(url_for('admin_users'))

@app.route('/admin/meals')
@admin_required
def admin_meals():
    q = request.args.get('q', '').strip()
    date_str = request.args.get('date', '').strip()
    query = Meal.query.join(User)
    if q:
        query = query.filter((Meal.food_name.ilike(f'%{q}%')) | (User.name.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%')))
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Meal.date_logged == filter_date)
        except ValueError:
            date_str = ''
        
    meals_raw = query.order_by(Meal.date_logged.desc(), Meal.id.desc()).all()
    meals = []
    for m in meals_raw:
        meals.append({
            "id": m.id,
            "user_id": m.user_id,
            "user_name": m.user.name if m.user else "Unknown User",
            "food_name": m.food_name,
            "calories": m.calories,
            "protein": m.protein,
            "carbs": m.carbs,
            "fats": m.fats,
            "vit_c": m.vit_c,
            "calcium": m.calcium,
            "iron": m.iron,
            "date_logged": m.date_logged.strftime('%Y-%m-%d') if m.date_logged else ""
        })
        
    return render_template('admin/meals.html', meals=meals, query=q, selected_date=date_str)

@app.route('/admin/meal/<int:meal_id>/delete', methods=['POST'])
@admin_required
def admin_delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    food_name = meal.food_name
    db.session.delete(meal)
    db.session.commit()
    flash(f"Meal log '{food_name}' was removed successfully.")
    
    redirect_to = request.args.get('redirect_to')
    user_id = request.args.get('user_id')
    if redirect_to == 'user' and user_id:
        return redirect(url_for('admin_user_meals', user_id=user_id))
    return redirect(url_for('admin_meals'))

@app.route('/admin/foods', methods=['GET', 'POST'])
@admin_required
def admin_foods():
    if request.method == 'POST':
        name = request.form.get('food_name', '').strip()
        try:
            calories = float(request.form.get('calories', 0))
            protein = float(request.form.get('protein', 0))
            carbs = float(request.form.get('carbs', 0))
            fats = float(request.form.get('fats', 0))
            vit_c = float(request.form.get('vit_c', 0))
            calcium = float(request.form.get('calcium', 0))
            iron = float(request.form.get('iron', 0))
            
            if name:
                success = add_custom_food(name, calories, protein, carbs, fats, vit_c, calcium, iron)
                if success:
                    flash(f"Food item '{name.title()}' added to database successfully!")
                else:
                    flash("Failed to add food item to CSV storage.")
            else:
                flash("Food name cannot be empty.")
        except ValueError:
            flash("Invalid nutritional values entered. Please provide valid numbers.")
            
        return redirect(url_for('admin_foods'))
        
    q = request.args.get('q', '').strip().lower()
    all_foods = get_all_foods()
    if q:
        foods = [f for f in all_foods if q in f['name'].lower()]
    else:
        foods = all_foods
        
    return render_template('admin/foods.html', foods=foods, query=q)

@app.route('/admin/food/delete', methods=['POST'])
@admin_required
def admin_delete_food():
    food_name = request.form.get('food_name', '').strip()
    if food_name and delete_custom_food(food_name):
        flash(f"Food item '{food_name}' was deleted from database.")
    else:
        flash(f"Could not delete '{food_name}'.")
    return redirect(url_for('admin_foods'))

if __name__ == '__main__':
    app.run(debug=True)
