from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'foodshare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String(120))
    profile_posts = db.relationship('Post', backref='author', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'location': self.location
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    food_type = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    location = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'food_type': self.food_type,
            'quantity': self.quantity,
            'location': self.location,
            'author': self.author.username,
            'timestamp': str(self.timestamp)
        }

class Garden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    plants = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'plants': self.plants,
            'timestamp': str(self.timestamp)
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    gardens = Garden.query.all()
    return render_template('index.html', gardens=gardens)

@app.route('/community')
def community():
    posts = Post.query.all()
    return render_template('community.html', posts=posts)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    gardens = Garden.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=user, posts=posts, gardens=gardens)

@app.route('/garden')
def garden():
    gardens = Garden.query.all()
    return render_template('garden.html', gardens=gardens)

# API Routes
@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'POST':
        data = request.json
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        data = request.json
        post = Post(
            title=data['title'],
            content=data['content'],
            food_type=data.get('food_type'),
            quantity=data.get('quantity'),
            location=data.get('location'),
            user_id=data['user_id']
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict()), 201
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])

@app.route('/api/gardens', methods=['GET', 'POST'])
def api_gardens():
    if request.method == 'POST':
        data = request.json
        garden = Garden(
            name=data['name'],
            description=data.get('description'),
            location=data.get('location'),
            plants=data.get('plants'),
            user_id=data['user_id']
        )
        db.session.add(garden)
        db.session.commit()
        return jsonify(garden.to_dict()), 201
    gardens = Garden.query.all()
    return jsonify([g.to_dict() for g in gardens])

if __name__ == '__main__':
    app.run(debug=True)