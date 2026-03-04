"""
Gym Analytics - Main Flask Application
A comprehensive gym management and analytics platform
"""

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
from functools import wraps
import json
import os

# Import configuration and models
from config import config
from models import db, User, Member, Trainer, Workout, DietPlan, MealLog, Attendance, Announcement

# Create Flask application
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# Context processor to make variables available to all templates
@app.context_processor
def inject_user():
    """Inject current user into all templates"""
    return dict(current_user=current_user)


# Custom decorators
def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def trainer_required(f):
    """Decorator for trainer-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'trainer']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ROUTES ====================

# Home / Landing Page
@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth.html', page='login')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'warning')
                return render_template('auth.html', page='login')
            
            login_user(user, remember=True)
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('auth.html', page='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'member')
        
        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if not first_name or not last_name:
            errors.append('Please enter your full name.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth.html', page='register')
        
        # Create user
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create member or trainer profile
            if role == 'member':
                member = Member(
                    user_id=user.id,
                    membership_start=date.today(),
                    membership_end=date.today() + timedelta(days=30)
                )
                db.session.add(member)
            elif role == 'trainer':
                trainer = Trainer(user_id=user.id)
                db.session.add(trainer)
            
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('auth.html', page='register')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    # Get statistics based on user role
    if current_user.role == 'admin':
        total_members = User.query.filter_by(role='member').count()
        total_trainers = User.query.filter_by(role='trainer').count()
        total_workouts = Workout.query.count()
        
        # Get attendance for today
        today = date.today()
        today_attendance = Attendance.query.filter_by(date=today).count()
        
        # Get recent workouts
        recent_workouts = Workout.query.order_by(Workout.workout_date.desc()).limit(5).all()
        
        # Get announcements
        announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(3).all()
        
    elif current_user.role == 'trainer':
        trainer = Trainer.query.filter_by(user_id=current_user.id).first()
        if trainer:
            total_workouts = Workout.query.filter_by(trainer_id=trainer.id).count()
            recent_workouts = Workout.query.filter_by(trainer_id=trainer.id).order_by(Workout.workout_date.desc()).limit(5).all()
        else:
            total_workouts = 0
            recent_workouts = []
        total_members = 0
        total_trainers = 0
        today_attendance = 0
        announcements = []
        
    else:  # member
        member = Member.query.filter_by(user_id=current_user.id).first()
        if member:
            total_workouts = Workout.query.filter_by(member_id=member.id).count()
            recent_workouts = Workout.query.filter_by(member_id=member.id).order_by(Workout.workout_date.desc()).limit(5).all()
            
            # Get meal logs for today
            today_meals = MealLog.query.filter(
                MealLog.member_id == member.id,
                MealLog.logged_at >= datetime.combine(date.today(), datetime.min.time())
            ).all()
            
            # Calculate today's calories
            today_calories = sum(meal.calories or 0 for meal in today_meals)
        else:
            total_workouts = 0
            recent_workouts = []
            today_calories = 0
        total_members = 0
        total_trainers = 0
        today_attendance = 0
        announcements = []
    
    # Get workout data for chart (last 7 days)
    workout_dates = []
    workout_counts = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        workout_dates.append(day.strftime('%a'))
        count = Workout.query.filter(
            db.func.date(Workout.workout_date) == day
        ).count()
        workout_counts.append(count)
    
    stats = {
        'total_members': total_members,
        'total_trainers': total_trainers,
        'total_workouts': total_workouts,
        'today_attendance': today_attendance,
        'today_calories': today_calories if current_user.role == 'member' else 0
    }
    
    return render_template('dashboard.html', 
                           stats=stats,
                           recent_workouts=recent_workouts,
                           announcements=announcements,
                           workout_dates=workout_dates,
                           workout_counts=workout_counts)


# Members
@app.route('/members')
@login_required
def members():
    """Members listing page"""
    if current_user.role not in ['admin', 'trainer']:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    search_query = request.args.get('search', '').strip()
    membership_filter = request.args.get('membership', '')
    
    # Base query
    query = User.query.filter_by(role='member')
    
    if search_query:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.first_name.ilike(f'%{search_query}%'),
                User.last_name.ilike(f'%{search_query}%')
            )
        )
    
    members_list = query.order_by(User.created_at.desc()).all()
    
    # Get member details
    members_data = []
    for user in members_list:
        member = Member.query.filter_by(user_id=user.id).first()
        if member:
            members_data.append({
                'user': user,
                'member': member
            })
    
    return render_template('members.html', members=members_data, search=search_query)


@app.route('/members/add', methods=['POST'])
@login_required
@admin_required
def add_member():
    """Add new member"""
    try:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', 'password123')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        membership_type = request.form.get('membership_type', 'basic')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('members'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('members'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='member'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create member profile
        member = Member(
            user_id=user.id,
            membership_type=membership_type,
            membership_start=date.today(),
            membership_end=date.today() + timedelta(days=30)
        )
        db.session.add(member)
        db.session.commit()
        
        flash(f'Member {user.get_full_name()} added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding member: {str(e)}', 'danger')
        print(f"Add member error: {e}")
    
    return redirect(url_for('members'))


# Workouts
@app.route('/workouts')
@login_required
def workouts():
    """Workouts listing page"""
    workout_type = request.args.get('type', '')
    date_filter = request.args.get('date', '')
    
    # Base query
    if current_user.role == 'member':
        member = Member.query.filter_by(user_id=current_user.id).first()
        if member:
            query = Workout.query.filter_by(member_id=member.id)
        else:
            query = Workout.query.filter_by(id=0)
    else:
        query = Workout.query
    
    if workout_type:
        query = query.filter_by(workout_type=workout_type)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Workout.workout_date) == filter_date)
        except:
            pass
    
    workouts_list = query.order_by(Workout.workout_date.desc()).limit(50).all()
    
    # Get workout types for filter
    workout_types = db.session.query(Workout.workout_type).distinct().all()
    workout_types = [w[0] for w in workout_types]
    
    return render_template('workouts.html', 
                           workouts=workouts_list, 
                           workout_types=workout_types,
                           selected_type=workout_type)


@app.route('/workouts/log', methods=['POST'])
@login_required
def log_workout():
    """Log a new workout"""
    try:
        member_id = request.form.get('member_id')
        workout_type = request.form.get('workout_type', '').strip()
        workout_name = request.form.get('workout_name', '').strip()
        duration = int(request.form.get('duration', 0))
        calories = int(request.form.get('calories', 0))
        intensity = request.form.get('intensity', 'medium')
        notes = request.form.get('notes', '').strip()
        
        if not workout_type or duration <= 0:
            flash('Please provide workout type and duration.', 'danger')
            return redirect(url_for('workouts'))
        
        # Get member ID
        if current_user.role == 'member':
            member = Member.query.filter_by(user_id=current_user.id).first()
            if not member:
                flash('Member profile not found.', 'danger')
                return redirect(url_for('workouts'))
            member_id = member.id
        elif not member_id:
            flash('Please select a member.', 'danger')
            return redirect(url_for('workouts'))
        
        # Get trainer ID if admin/trainer
        trainer_id = None
        if current_user.role in ['admin', 'trainer']:
            trainer = Trainer.query.filter_by(user_id=current_user.id).first()
            if trainer:
                trainer_id = trainer.id
        
        # Create workout
        workout = Workout(
            member_id=member_id,
            trainer_id=trainer_id,
            workout_type=workout_type,
            workout_name=workout_name or workout_type.title(),
            duration_minutes=duration,
            calories_burned=calories,
            intensity=intensity,
            notes=notes,
            workout_date=datetime.now()
        )
        db.session.add(workout)
        db.session.commit()
        
        flash('Workout logged successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error logging workout: {str(e)}', 'danger')
        print(f"Log workout error: {e}")
    
    return redirect(url_for('workouts'))


# Diet Plans
@app.route('/diet')
@login_required
def diet():
    """Diet plans page"""
    if current_user.role == 'member':
        member = Member.query.filter_by(user_id=current_user.id).first()
        if member:
            diet_plans = DietPlan.query.filter_by(member_id=member.id).order_by(DietPlan.created_at.desc()).all()
            meal_logs = MealLog.query.filter_by(member_id=member.id).order_by(MealLog.logged_at.desc()).limit(20).all()
        else:
            diet_plans = []
            meal_logs = []
    else:
        diet_plans = DietPlan.query.order_by(DietPlan.created_at.desc()).limit(20).all()
        meal_logs = []
    
    return render_template('diet.html', diet_plans=diet_plans, meal_logs=meal_logs)


@app.route('/diet/plan/add', methods=['POST'])
@login_required
def add_diet_plan():
    """Add a new diet plan"""
    try:
        plan_name = request.form.get('plan_name', '').strip()
        plan_type = request.form.get('plan_type', 'maintenance')
        daily_calories = int(request.form.get('daily_calories', 2000))
        daily_protein = float(request.form.get('daily_protein', 50))
        daily_carbs = float(request.form.get('daily_carbs', 250))
        daily_fat = float(request.form.get('daily_fat', 65))
        description = request.form.get('description', '').strip()
        
        if not plan_name:
            flash('Please provide a plan name.', 'danger')
            return redirect(url_for('diet'))
        
        # Get member ID
        if current_user.role == 'member':
            member = Member.query.filter_by(user_id=current_user.id).first()
            if not member:
                flash('Member profile not found.', 'danger')
                return redirect(url_for('diet'))
            member_id = member.id
        else:
            flash('Only members can create diet plans.', 'danger')
            return redirect(url_for('diet'))
        
        # Create diet plan
        diet_plan = DietPlan(
            member_id=member_id,
            plan_name=plan_name,
            plan_type=plan_type,
            daily_calories=daily_calories,
            daily_protein=daily_protein,
            daily_carbs=daily_carbs,
            daily_fat=daily_fat,
            description=description,
            start_date=date.today(),
            is_active=True
        )
        db.session.add(diet_plan)
        db.session.commit()
        
        flash('Diet plan created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating diet plan: {str(e)}', 'danger')
        print(f"Add diet plan error: {e}")
    
    return redirect(url_for('diet'))


@app.route('/diet/log', methods=['POST'])
@login_required
def log_meal():
    """Log a meal"""
    try:
        meal_type = request.form.get('meal_type', '').strip()
        meal_name = request.form.get('meal_name', '').strip()
        calories = int(request.form.get('calories', 0))
        protein = float(request.form.get('protein', 0))
        carbs = float(request.form.get('carbs', 0))
        fat = float(request.form.get('fat', 0))
        
        if not meal_type or calories < 0:
            flash('Please provide meal type and calories.', 'danger')
            return redirect(url_for('diet'))
        
        # Get member ID
        if current_user.role == 'member':
            member = Member.query.filter_by(user_id=current_user.id).first()
            if not member:
                flash('Member profile not found.', 'danger')
                return redirect(url_for('diet'))
            member_id = member.id
        else:
            flash('Only members can log meals.', 'danger')
            return redirect(url_for('diet'))
        
        # Create meal log
        meal = MealLog(
            member_id=member_id,
            meal_type=meal_type,
            meal_name=meal_name,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            logged_at=datetime.now()
        )
        db.session.add(meal)
        db.session.commit()
        
        flash('Meal logged successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error logging meal: {str(e)}', 'danger')
        print(f"Log meal error: {e}")
    
    return redirect(url_for('diet'))


# Analytics
@app.route('/analytics')
@login_required
def analytics():
    """Analytics page with charts"""
    # Get date range (last 30 days by default)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    if current_user.role == 'admin':
        # Member growth data
        member_counts = []
        member_dates = []
        for i in range(30, -1, -5):
            day = end_date - timedelta(days=i)
            count = User.query.filter(
                User.role == 'member',
                User.created_at <= datetime.combine(day, datetime.max.time())
            ).count()
            member_dates.append(day.strftime('%b %d'))
            member_counts.append(count)
        
        # Workout type distribution
        workout_types = db.session.query(
            Workout.workout_type,
            db.func.count(Workout.id)
        ).group_by(Workout.workout_type).all()
        
        # Attendance data
        attendance_data = []
        for i in range(6, -1, -1):
            day = end_date - timedelta(days=i)
            count = Attendance.query.filter_by(date=day).count()
            attendance_data.append(count)
        
        # Revenue estimation (mock data based on memberships)
        membership_revenue = {
            'basic': Member.query.filter_by(membership_type='basic').count() * 500,
            'premium': Member.query.filter_by(membership_type='premium').count() * 1000,
            'vip': Member.query.filter_by(membership_type='vip').count() * 2000
        }
        
        total_members = User.query.filter_by(role='member').count()
        active_members = Member.query.filter(Member.membership_end >= date.today()).count()
        
    elif current_user.role == 'member':
        member = Member.query.filter_by(user_id=current_user.id).first()
        if member:
            # Weight progress
            workouts = Workout.query.filter_by(member_id=member.id).order_by(Workout.workout_date).all()
            
            # Calories over time
            meals = MealLog.query.filter(
                MealLog.member_id == member.id,
                MealLog.logged_at >= datetime.combine(start_date, datetime.min.time())
            ).order_by(MealLog.logged_at).all()
            
            # Group by date
            calorie_by_date = {}
            for meal in meals:
                day_key = meal.logged_at.strftime('%Y-%m-%d')
                if day_key not in calorie_by_date:
                    calorie_by_date[day_key] = 0
                calorie_by_date[day_key] += meal.calories or 0
            
            member_dates = list(calorie_by_date.keys())[-10:] or []
            member_counts = list(calorie_by_date.values())[-10:] or []
            
            workout_types = db.session.query(
                Workout.workout_type,
                db.func.count(Workout.id)
            ).filter(Workout.member_id == member.id).group_by(Workout.workout_type).all()
            
            attendance_data = []
            for i in range(6, -1, -1):
                day = end_date - timedelta(days=i)
                count = Attendance.query.filter_by(member_id=member.id, date=day).count()
                attendance_data.append(count)
            
            total_workouts = Workout.query.filter_by(member_id=member.id).count()
            total_meals = MealLog.query.filter_by(member_id=member.id).count()
            
            member = member
            total_members = total_workouts
            active_members = total_meals
            membership_revenue = {}
        else:
            member_dates = []
            member_counts = []
            workout_types = []
            attendance_data = []
            total_members = 0
            active_members = 0
            membership_revenue = {}
            member = None
    else:
        member_dates = []
        member_counts = []
        workout_types = []
        attendance_data = []
        total_members = 0
        active_members = 0
        membership_revenue = {}
        member = None
    
    return render_template('analytics.html',
                          member_dates=member_dates,
                          member_counts=member_counts,
                          workout_types=workout_types,
                          attendance_data=attendance_data,
                          membership_revenue=membership_revenue,
                          total_members=total_members,
                          active_members=active_members,
                          member=member if current_user.role == 'member' else None)


# API Routes for AJAX
@app.route('/api/member/<int:member_id>')
@login_required
def get_member(member_id):
    """Get member details as JSON"""
    member = Member.query.get_or_404(member_id)
    user = User.query.get(member.user_id)
    
    return jsonify({
        'user': user.to_dict(),
        'member': member.to_dict()
    })


@app.route('/api/stats')
@login_required
def get_stats():
    """Get dashboard stats as JSON"""
    if current_user.role == 'admin':
        stats = {
            'total_members': User.query.filter_by(role='member').count(),
            'total_trainers': User.query.filter_by(role='trainer').count(),
            'total_workouts': Workout.query.count(),
            'today_attendance': Attendance.query.filter_by(date=date.today()).count()
        }
    else:
        stats = {'error': 'Unauthorized'}
    
    return jsonify(stats)


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('index.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('index.html', error='Internal server error'), 500


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@gymanalytics.com',
                first_name='Admin',
                last_name='User',
                phone='1234567890',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")
        
        # Check if demo member exists
        demo_member = User.query.filter_by(username='demo').first()
        if not demo_member:
            demo_member = User(
                username='demo',
                email='demo@gymanalytics.com',
                first_name='Demo',
                last_name='User',
                phone='9876543210',
                role='member'
            )
            demo_member.set_password('demo123')
            db.session.add(demo_member)
            db.session.flush()
            
            member = Member(
                user_id=demo_member.id,
                membership_type='premium',
                membership_start=date.today(),
                membership_end=date.today() + timedelta(days=365),
                height=175,
                weight=75,
                target_weight=70,
                fitness_goal='weight_loss'
            )
            db.session.add(member)
            db.session.commit()
            print("Demo member created: demo / demo123")


# Run the application
if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

