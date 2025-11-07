from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json
import time
from datetime import datetime, timedelta
import threading
from collections import defaultdict
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'foodshare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure file uploads
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# Request deduplication - stores locks for in-progress requests
request_locks = {}
locks_mutex = threading.Lock()

# Queue to collect duplicate requests
request_queues = defaultdict(list)
queue_mutex = threading.Lock()

def clean_old_requests():
    """Remove old locks"""
    pass  # Not needed with locks

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    image_url = db.Column(db.String(300))  # Added for image uploads
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    likes = db.Column(db.Integer, default=0)  # Added for like functionality
    replies = db.relationship('Reply', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'food_type': self.food_type,
            'quantity': self.quantity,
            'location': self.location,
            'image_url': self.image_url,
            'author': self.author.username,
            'likes': self.likes,
            'timestamp': str(self.timestamp),
            'reply_count': len(self.replies)
        }

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    author = db.relationship('User', backref='replies', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.username,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'timestamp': str(self.timestamp)
        }

class Garden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
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
    plot_index = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='available')
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
    posts = Post.query.order_by(Post.timestamp.desc()).all()
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
        # Get form data (not JSON because we're receiving multipart/form-data with file)
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        food_type = request.form.get('food_type', '')
        quantity = request.form.get('quantity', '')
        location = request.form.get('location', '')
        user_id = request.form.get('user_id', 1)
        
        # Validate required fields
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Create a unique key for this post (title + user_id)
        request_key = f"post_{user_id}_{title[:50]}"
        
        # Add this request to the queue
        with queue_mutex:
            request_queues[request_key].append(request.form.to_dict())
            queue_size = len(request_queues[request_key])
            print(f"📥 Post request {queue_size} for '{title}' added to queue")
        
        # Get or create a lock for this post
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            post_lock = request_locks[request_key]
        
        # Try to acquire the lock
        lock_acquired = post_lock.acquire(blocking=False)
        
        if not lock_acquired:
            # Another request is already processing, wait for it
            print(f"⏳ Waiting for other post request to finish for '{title}'...")
            post_lock.acquire()  # Wait for the lock
            post_lock.release()  # Immediately release it
            
            # Find the post that was just created
            recent_post = Post.query.filter_by(
                title=title,
                user_id=user_id
            ).order_by(Post.timestamp.desc()).first()
            
            if recent_post:
                print(f"✅ Returning existing post '{title}'")
                return jsonify(recent_post.to_dict()), 201
            else:
                return jsonify({'error': 'Post creation failed'}), 500
        
        try:
            print(f"🔒 Lock acquired for post '{title}', processing...")
            
            # Wait briefly for duplicate requests to arrive
            time.sleep(0.15)  # 150ms wait
            
            # Get all requests from queue and pick the FIRST one (as requested)
            with queue_mutex:
                all_requests = request_queues[request_key]
                best_request = all_requests[0] if all_requests else request.form.to_dict()
                print(f"📊 Processing first of {len(all_requests)} duplicate post requests")
                # Clear the queue
                request_queues[request_key] = []
            
            # Handle image upload
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    # Create a secure filename
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    
                    # Save file
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_filename = filename
                    print(f"📸 Saved image: {filename}")
            
            # Create post using the first request data
            post = Post(
                title=title,
                content=content,
                food_type=food_type,
                quantity=quantity,
                location=location,
                image_url=image_filename,
                user_id=user_id
            )
            db.session.add(post)
            db.session.commit()
            
            print(f"✅ Post created: {title}")
            return jsonify(post.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating post: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            post_lock.release()
            print(f"🔓 Lock released for post '{title}'")
    
    # GET request - return all posts
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify([p.to_dict() for p in posts])

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Increment the like count for a post"""
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

@app.route('/api/posts/<int:post_id>/replies', methods=['GET', 'POST'])
def post_replies(post_id):
    """Get all replies for a post or create a new reply"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        data = request.json
        content = data.get('content', '').strip()
        user_id = data.get('user_id', 1)
        
        # Validate required fields
        if not content:
            return jsonify({'error': 'Reply content is required'}), 400
        
        # Create a unique key for this reply (content + post_id + user_id)
        request_key = f"reply_{post_id}_{user_id}_{content[:50]}"
        
        # Add this request to the queue
        with queue_mutex:
            request_queues[request_key].append(data)
            queue_size = len(request_queues[request_key])
            print(f"📥 Reply request {queue_size} for post {post_id} added to queue")
        
        # Get or create a lock for this reply
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            reply_lock = request_locks[request_key]
        
        # Try to acquire the lock
        lock_acquired = reply_lock.acquire(blocking=False)
        
        if not lock_acquired:
            # Another request is already processing, wait for it
            print(f"⏳ Waiting for other reply request to finish for post {post_id}...")
            reply_lock.acquire()  # Wait for the lock
            reply_lock.release()  # Immediately release it
            
            # Find the reply that was just created
            recent_reply = Reply.query.filter_by(
                post_id=post_id,
                user_id=user_id,
                content=content
            ).order_by(Reply.timestamp.desc()).first()
            
            if recent_reply:
                print(f"✅ Returning existing reply for post {post_id}")
                return jsonify(recent_reply.to_dict()), 201
            else:
                return jsonify({'error': 'Reply creation failed'}), 500
        
        try:
            print(f"🔒 Lock acquired for reply to post {post_id}, processing...")
            
            # Wait briefly for duplicate requests to arrive
            time.sleep(0.15)  # 150ms wait
            
            # Get all requests from queue and pick the last one (most complete)
            with queue_mutex:
                all_requests = request_queues[request_key]
                best_request = all_requests[-1] if all_requests else data
                print(f"📊 Processing last of {len(all_requests)} duplicate reply requests")
                # Clear the queue
                request_queues[request_key] = []
            
            # Use the best request data
            data = best_request
            content = data.get('content', '').strip()
            user_id = data.get('user_id', 1)
            
            # Create reply
            reply = Reply(
                content=content,
                user_id=user_id,
                post_id=post_id
            )
            db.session.add(reply)
            db.session.commit()
            
            print(f"✅ Reply created for post {post_id}")
            return jsonify(reply.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating reply: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            reply_lock.release()
            print(f"🔓 Lock released for reply to post {post_id}")
    
    # GET request - return all replies for this post
    replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.timestamp.asc()).all()
    return jsonify([r.to_dict() for r in replies])

@app.route('/api/gardens', methods=['GET', 'POST'])
def api_gardens():
    if request.method == 'POST':
        data = request.json
        garden_name = data['name'].strip()
        
        # Validate garden name is not empty
        if not garden_name:
            return jsonify({'error': 'Garden name is required'}), 400
        
        # Create a unique key for this garden
        request_key = garden_name.lower()
        
        # Add this request to the queue
        with queue_mutex:
            request_queues[request_key].append(data)
            queue_size = len(request_queues[request_key])
            print(f"📥 Request {queue_size} for '{garden_name}' added to queue")
        
        # Get or create a lock for this garden name
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            garden_lock = request_locks[request_key]
        
        # Try to acquire the lock
        lock_acquired = garden_lock.acquire(blocking=False)
        
        if not lock_acquired:
            # Another request is already processing, wait for it
            print(f"⏳ Waiting for other request to finish for '{garden_name}'...")
            garden_lock.acquire()  # Wait for the lock
            garden_lock.release()  # Immediately release it
            
            # Check if garden was created
            existing_garden = Garden.query.filter_by(name=garden_name).first()
            if existing_garden:
                print(f"✅ Garden '{garden_name}' already created by another request")
                return jsonify(existing_garden.to_dict()), 200
            else:
                print(f"⚠️  Garden '{garden_name}' not found after waiting")
                return jsonify({'error': 'Garden creation failed'}), 500
        
        try:
            print(f"🔒 Lock acquired for '{garden_name}', processing...")
            
            # Wait briefly for duplicate requests to arrive
            time.sleep(0.15)  # 150ms wait
            
            # Get all requests from queue and pick the best one
            with queue_mutex:
                all_requests = request_queues[request_key]
                print(f"📊 Found {len(all_requests)} request(s) in queue")
                
                # Pick the request with the most plot_states data
                best_request = max(all_requests, key=lambda r: len(r.get('plot_states', [])))
                plot_states_len = len(best_request.get('plot_states', []))
                print(f"🎯 Selected best request with {plot_states_len} plot states")
                
                # Clear the queue
                del request_queues[request_key]
            
            # Use the best request data
            data = best_request
            
            # Check if garden already exists
            existing_garden = Garden.query.filter_by(name=garden_name).first()
            if existing_garden:
                print(f"⚠️  Garden '{garden_name}' already exists")
                return jsonify(existing_garden.to_dict()), 200
            
            # Create the garden with the best data
            rows = data.get('rows', 5)
            cols = data.get('cols', 5)
            plot_states = data.get('plot_states', [])
            
            print(f"📊 Creating garden with plot_states length: {len(plot_states)}")
            
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
            db.session.flush()
            
            # Create garden plots
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
            print(f"✅ Successfully created garden '{garden_name}'")
            return jsonify(garden.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating garden: {e}")
            return jsonify({'error': 'Failed to create garden'}), 500
        finally:
            garden_lock.release()
            # Clean up
            with locks_mutex:
                if request_key in request_locks:
                    del request_locks[request_key]
            
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
    app.run(debug=False, port=5000)