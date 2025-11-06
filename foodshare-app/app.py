from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'foodshare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Request deduplication cache - stores recent garden creation requests
recent_requests = {}

def clean_old_requests():
    """Remove requests older than 5 seconds"""
    current_time = time.time()
    to_remove = [key for key, timestamp in recent_requests.items() if current_time - timestamp > 5]
    for key in to_remove:
        del recent_requests[key]

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
    name = db.Column(db.String(120), nullable=False, unique=True)  # Make name unique
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    plants = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rows = db.Column(db.Integer, default=5)
    cols = db.Column(db.Integer, default=5)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    plots = db.relationship('GardenPlot', backref='garden', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'plants': self.plants,
            'rows': self.rows,
            'cols': self.cols,
            'timestamp': str(self.timestamp)
        }

class GardenPlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey('garden.id'), nullable=False)
    plot_index = db.Column(db.Integer, nullable=False)  # Position in grid (0 to rows*cols-1)
    status = db.Column(db.String(20), default='available')  # available, taken, mine, null
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    claimed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        owner_name = None
        if self.user_id:
            user = User.query.get(self.user_id)
            owner_name = user.username if user else None
            
        return {
            'id': self.id,
            'garden_id': self.garden_id,
            'plot_index': self.plot_index,
            'status': self.status,
            'user_id': self.user_id,
            'owner': owner_name,
            'claimed_at': str(self.claimed_at) if self.claimed_at else None
        }

# Routes
@app.route('/')
def index():
    gardens = Garden.query.all()
    return render_template('index.html', gardens=gardens)

@app.route('/community')
def community():
    posts = Post.query.all()
    return render_template('community.html', posts=posts)

@app.route('/profile')
@app.route('/profile/<int:user_id>')
def profile(user_id=1):
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
        garden_name = data['name']
        
        # Clean old requests
        clean_old_requests()
        
        # Create a unique key for this request
        request_key = f"{garden_name}_{data.get('location')}_{data['user_id']}"
        
        # Check if this exact request was made in the last 5 seconds
        if request_key in recent_requests:
            print(f"Duplicate request detected for '{garden_name}', ignoring")
            # Return existing garden
            existing = Garden.query.filter_by(name=garden_name).first()
            if existing:
                return jsonify(existing.to_dict()), 200
            # If somehow doesn't exist, allow this request through
        
        # Mark this request as being processed
        recent_requests[request_key] = time.time()
        
        # Check if garden with same name already exists
        existing_garden = Garden.query.filter_by(name=garden_name).first()
        if existing_garden:
            return jsonify({'error': 'A garden with this name already exists'}), 400
        
        rows = data.get('rows', 5)
        cols = data.get('cols', 5)
        plot_states = data.get('plot_states', [])
        
        try:
            garden = Garden(
                name=garden_name,
                description=data.get('description'),
                location=data.get('location'),
                plants=data.get('plants'),
                user_id=data['user_id'],
                rows=rows,
                cols=cols
            )
            db.session.add(garden)
            db.session.flush()  # Get the garden ID
            
            # Create garden plots based on designer configuration
            total_plots = rows * cols
            
            for i in range(total_plots):
                if plot_states and i < len(plot_states):
                    status = plot_states[i]
                else:
                    is_null = (i == 0 or i == cols - 1 or i == total_plots - cols or i == total_plots - 1)
                    status = 'null' if is_null else 'available'
                
                plot = GardenPlot(
                    garden_id=garden.id,
                    plot_index=i,
                    status=status
                )
                db.session.add(plot)
            
            db.session.commit()
            print(f"Successfully created garden '{garden_name}'")
            return jsonify(garden.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            # Remove from cache on error
            if request_key in recent_requests:
                del recent_requests[request_key]
            # Check if it's a unique constraint violation
            if 'UNIQUE constraint failed' in str(e) or 'unique' in str(e).lower():
                return jsonify({'error': 'A garden with this name already exists'}), 400
            print(f"Error creating garden: {e}")
            return jsonify({'error': str(e)}), 500
            
    gardens = Garden.query.all()
    return jsonify([g.to_dict() for g in gardens])

@app.route('/api/gardens/<int:garden_id>/plots', methods=['GET'])
def get_garden_plots(garden_id):
    garden = Garden.query.get_or_404(garden_id)
    plots = GardenPlot.query.filter_by(garden_id=garden_id).order_by(GardenPlot.plot_index).all()
    
    # Determine status for each plot (for current user - using demo user id=1)
    current_user_id = 1
    plots_data = []
    
    for plot in plots:
        plot_dict = plot.to_dict()
        # Update status to show 'mine' if current user owns it
        if plot.user_id == current_user_id and plot.status == 'taken':
            plot_dict['status'] = 'mine'
        plots_data.append(plot_dict)
    
    return jsonify({
        'garden_id': garden.id,
        'garden_name': garden.name,
        'rows': garden.rows,
        'cols': garden.cols,
        'plots': plots_data
    })

@app.route('/api/gardens/<int:garden_id>/plots/<int:plot_index>/claim', methods=['POST'])
def claim_plot(garden_id, plot_index):
    data = request.json
    user_id = data.get('user_id', 1)
    
    plot = GardenPlot.query.filter_by(garden_id=garden_id, plot_index=plot_index).first()
    
    if not plot:
        return jsonify({'success': False, 'error': 'Plot not found'}), 404
    
    if plot.status != 'available':
        return jsonify({'success': False, 'error': 'Plot is not available'}), 400
    
    plot.status = 'taken'
    plot.user_id = user_id
    plot.claimed_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({'success': True, 'plot': plot.to_dict()})

@app.route('/api/gardens/<int:garden_id>/plots/<int:plot_index>/release', methods=['POST'])
def release_plot(garden_id, plot_index):
    data = request.json
    user_id = data.get('user_id', 1)
    
    plot = GardenPlot.query.filter_by(garden_id=garden_id, plot_index=plot_index).first()
    
    if not plot:
        return jsonify({'success': False, 'error': 'Plot not found'}), 404
    
    if plot.user_id != user_id:
        return jsonify({'success': False, 'error': 'You do not own this plot'}), 403
    
    plot.status = 'available'
    plot.user_id = None
    plot.claimed_at = None
    
    db.session.commit()
    
    return jsonify({'success': True, 'plot': plot.to_dict()})

if __name__ == '__main__':
    import os
    
    # Only initialize database on the main process, not the reloader
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        with app.app_context():
            db.create_all()
            # Create default user if doesn't exist
            if User.query.filter_by(username='demo').first() is None:
                demo_user = User(username='demo', email='demo@foodshare.com', bio='Demo user', location='Clemson, SC')
                db.session.add(demo_user)
                db.session.commit()
    
    # Run WITHOUT debug mode to prevent duplicate requests
    # Note: You'll need to manually restart the server when you make code changes
    app.run(debug=False, port=5000)