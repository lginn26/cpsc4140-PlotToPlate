FoodShare
A web application that connects communities to share food and gardens.
Quick Start
Prerequisites: Python 3.8+
Installation:

cd foodshare-app
python -m venv venv
source venv/bin/activate (macOS/Linux) or venv\Scripts\activate (Windows)
pip install -r requirements.txt
python app.py
Open http://localhost:5000

Features

Create and browse community gardens
Share surplus food with neighbors
User profiles with garden and post history
Responsive design

Project Structure  
```
foodshare-app/  
├── app.py                 (Flask app, routes, models)  
├── requirements.txt       (Python dependencies)  
├── database/  
│   └── foodshare.db      (SQLite database)  
├── static/  
│   ├── css/main.css      (All styles)  
│   └── js/script.js      (Form handlers)  
└── templates/  
├── base.html         (Master template)  
├── index.html        (Home)  
├── garden.html       (Gardens)  
├── community.html    (Posts)  
└── profile.html      (User profile)  
```

Database
Three tables: User, Garden, Post
User: id, username, email, bio, location
Garden: id, name, description, location, plants, user_id, timestamp
Post: id, title, content, food_type, quantity, location, user_id, timestamp
API Endpoints
GET/POST /api/users
GET/POST /api/gardens
GET/POST /api/posts
GET / (home)
GET /garden (gardens page)
GET /community (posts page)
GET /profile/<user_id> (user profile)
Tech Stack
Flask, SQLite, SQLAlchemy, Bootstrap 5, Font Awesome, JavaScript
Color Palette
Primary: #1B5E3F
Dark: #0F4C2F
Light Background: #F5F5F5
Text Dark: #333333
Text Light: #666666
