# Gym Analytics - Project Specification

## 1. Project Overview

**Project Name:** Gym Analytics  
**Project Type:** Full-stack Web Application  
**Core Functionality:** A comprehensive gym management and analytics platform that tracks workouts, diets, member profiles, progress analytics, and gym operations similar to Gymflo.in  
**Target Users:** Gym owners, trainers, and gym members

---

## 2. Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom styling with animations
- **JavaScript (ES6+)** - Interactive functionality
- **Chart.js** - Analytics visualizations

### Backend
- **Python Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - Authentication

### Database
- **SQLite** - Local database (for portability)

---

## 3. UI/UX Specification

### Color Palette
- **Primary:** #0f0f0f (Deep Black)
- **Secondary:** #1a1a2e (Dark Navy)
- **Accent:** #e94560 (Vibrant Red)
- **Accent Secondary:** #16c79a (Teal Green)
- **Text Primary:** #ffffff (White)
- **Text Secondary:** #a0a0a0 (Gray)
- **Card Background:** #16213e (Dark Blue)
- **Gradient:** linear-gradient(135deg, #1a1a2e 0%, #0f0f0f 100%)

### Typography
- **Primary Font:** 'Orbitron', sans-serif (Headings - futuristic gym feel)
- **Secondary Font:** 'Rajdhani', sans-serif (Body text - clean, modern)
- **Font Sizes:**
  - H1: 3rem
  - H2: 2.5rem
  - H3: 1.8rem
  - Body: 1rem
  - Small: 0.875rem

### Layout Structure
- **Navigation:** Fixed top navbar with logo, menu links, user profile
- **Hero Section:** Full-width banner with CTA buttons
- **Content Sections:** Card-based grid layouts
- **Footer:** Multi-column footer with links and social media

### Responsive Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Visual Effects
- **Card Hover:** Scale 1.05, box-shadow increase
- **Button Hover:** Background shift, subtle glow
- **Page Transitions:** Fade-in animations
- **Loading States:** Pulse animations on cards

---

## 4. Page Structure

### 4.1 Landing Page (index.html)
- Hero section with animated background
- Features overview (4 cards)
- Services section
- Testimonials
- CTA sections
- Footer

### 4.2 Dashboard (dashboard.html)
- Quick stats cards (Members, Trainers, Workouts Today, Revenue)
- Recent workouts table
- Attendance chart (Chart.js)
- Quick actions panel

### 4.3 Members (members.html)
- Member listing with search/filter
- Member profile cards
- Add new member modal
- Member details view

### 4.4 Workouts (workouts.html)
- Workout categories (Strength, Cardio, HIIT, etc.)
- Exercise library
- Workout logging form
- Progress tracking

### 4.5 Diet Plans (diet.html)
- Diet plan templates
- Meal logging
- Calorie tracking
- Nutrition analytics

### 4.6 Analytics (analytics.html)
- Member growth chart
- Workout frequency chart
- Revenue analytics
- BMI/Progress charts

### 4.7 Login/Register (auth.html)
- Login form
- Registration form
- Form validation
- Error handling

---

## 5. Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- first_name
- last_name
- phone
- role (admin/trainer/member)
- profile_image
- created_at
- updated_at

### Members Table
- id (Primary Key)
- user_id (Foreign Key)
- membership_type
- membership_start
- membership_end
- height
- weight
- target_weight
- emergency_contact
- medical_conditions

### Workouts Table
- id (Primary Key)
- member_id (Foreign Key)
- trainer_id (Foreign Key)
- workout_type
- duration_minutes
- calories_burned
- exercises (JSON)
- notes
- workout_date

### Diet Plans Table
- id (Primary Key)
- member_id (Foreign Key)
- plan_name
- daily_calories
- meals (JSON)
- start_date
- end_date
- is_active

### Meal Logs Table
- id (Primary Key)
- member_id (Foreign Key)
- meal_type (breakfast/lunch/dinner/snack)
- food_items (JSON)
- calories
- protein
- carbs
- fat
- logged_at

### Attendance Table
- id (Primary Key)
- member_id (Foreign Key)
- check_in
- check_out
- date

---

## 6. Feature List

### Core Features
1. User Authentication (Login/Register/Logout)
2. Dashboard with real-time statistics
3. Member Management (CRUD operations)
4. Workout Logging and Tracking
5. Diet Plan Management
6. Meal Logging
7. Progress Analytics with Charts
8. Attendance Tracking
9. Search and Filter functionality
10. Responsive Design

### Admin Features
- Full system access
- Member management
- View all analytics
- Manage trainers

### Trainer Features
- Log workouts for members
- Create diet plans
- View member progress

### Member Features
- View own profile
- Log workouts
- Track diet
- View personal analytics

---

## 7. Acceptance Criteria

1. ✓ Website loads without errors
2. ✓ All pages are responsive
3. ✓ Navigation works correctly
4. ✓ Forms validate input
5. ✓ Database operations work
6. ✓ Charts display correctly
7. ✓ Animations are smooth
8. ✓ Colors and fonts match specification
9. ✓ No console errors
10. ✓ All features functional

---

## 8. File Structure

```
Gym Analytics/
├── app.py                 # Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js       # Main JavaScript
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Landing page
    ├── dashboard.html     # Dashboard
    ├── members.html       # Members page
    ├── workouts.html      # Workouts page
    ├── diet.html          # Diet plans page
    ├── analytics.html     # Analytics page
    └── auth.html          # Login/Register
```

---

## 9. External Resources

### CDN Links
- Google Fonts: Orbitron, Rajdhani
- Chart.js: https://cdn.jsdelivr.net/npm/chart.js
- Font Awesome: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css

---

*Document Version: 1.0*
*Created for: Gym Analytics Mini Project*

