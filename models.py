from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='member')  # admin, trainer, member
    profile_image = db.Column(db.String(255), default='default-avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    member_profile = db.relationship('Member', backref='user', uselist=False, lazy=True)
    trainer_profile = db.relationship('Trainer', backref='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone': self.phone,
            'role': self.role,
            'profile_image': self.profile_image,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Member(db.Model):
    """Member profile extended from user"""
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    membership_type = db.Column(db.String(50), default='basic')  # basic, premium, vip
    membership_start = db.Column(db.Date, nullable=False)
    membership_end = db.Column(db.Date)
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    target_weight = db.Column(db.Float)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    medical_conditions = db.Column(db.Text)
    fitness_goal = db.Column(db.String(100))  # weight_loss, muscle_gain, endurance, general_fitness
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workouts = db.relationship('Workout', backref='member', lazy=True, cascade='all, delete-orphan')
    diet_plans = db.relationship('DietPlan', backref='member', lazy=True, cascade='all, delete-orphan')
    meal_logs = db.relationship('MealLog', backref='member', lazy=True, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='member', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'membership_type': self.membership_type,
            'membership_start': self.membership_start.isoformat() if self.membership_start else None,
            'membership_end': self.membership_end.isoformat() if self.membership_end else None,
            'height': self.height,
            'weight': self.weight,
            'target_weight': self.target_weight,
            'fitness_goal': self.fitness_goal,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'medical_conditions': self.medical_conditions
        }


class Trainer(db.Model):
    """Trainer profile extended from user"""
    __tablename__ = 'trainers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(100))  # strength, cardio, yoga, etc.
    experience_years = db.Column(db.Integer, default=0)
    certification = db.Column(db.String(255))
    hourly_rate = db.Column(db.Float)
    bio = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workouts = db.relationship('Workout', backref='trainer', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'certification': self.certification,
            'hourly_rate': self.hourly_rate,
            'bio': self.bio,
            'is_available': self.is_available
        }


class Workout(db.Model):
    """Workout session model"""
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    workout_type = db.Column(db.String(50), nullable=False)  # strength, cardio, hiit, yoga, etc.
    workout_name = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer)
    intensity = db.Column(db.String(20))  # low, medium, high
    exercises = db.Column(db.Text)  # JSON string of exercises
    notes = db.Column(db.Text)
    workout_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'trainer_id': self.trainer_id,
            'workout_type': self.workout_type,
            'workout_name': self.workout_name,
            'duration_minutes': self.duration_minutes,
            'calories_burned': self.calories_burned,
            'intensity': self.intensity,
            'exercises': self.exercises,
            'notes': self.notes,
            'workout_date': self.workout_date.isoformat() if self.workout_date else None
        }


class DietPlan(db.Model):
    """Diet plan model"""
    __tablename__ = 'diet_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    plan_type = db.Column(db.String(50))  # weight_loss, muscle_gain, maintenance, custom
    daily_calories = db.Column(db.Integer)
    daily_protein = db.Column(db.Float)  # in grams
    daily_carbs = db.Column(db.Float)  # in grams
    daily_fat = db.Column(db.Float)  # in grams
    meals = db.Column(db.Text)  # JSON string of meal plans
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'daily_calories': self.daily_calories,
            'daily_protein': self.daily_protein,
            'daily_carbs': self.daily_carbs,
            'daily_fat': self.daily_fat,
            'meals': self.meals,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active
        }


class MealLog(db.Model):
    """Meal logging model"""
    __tablename__ = 'meal_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    meal_name = db.Column(db.String(100))
    food_items = db.Column(db.Text)  # JSON string
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'meal_type': self.meal_type,
            'meal_name': self.meal_name,
            'food_items': self.food_items,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }


class Attendance(db.Model):
    """Attendance tracking model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes
        }


class Announcement(db.Model):
    """Gym announcements"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

