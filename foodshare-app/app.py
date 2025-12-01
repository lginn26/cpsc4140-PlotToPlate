from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import time
from datetime import datetime
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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# Request deduplication
request_locks = {}
locks_mutex = threading.Lock()
request_queues = defaultdict(list)
queue_mutex = threading.Lock()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
#       DATABASE MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String(120))
    
    # Enhanced fields for guest mode and tracking
    role = db.Column(db.String(50), default='Garden Volunteer')
    is_guest = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    # Simple profile stats fields (optional defaults)
    plant_count = db.Column(db.Integer, default=0)
    zone = db.Column(db.String(50), default="Zone 3")
    friends = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)

    profile_posts = db.relationship('Post', backref='author', lazy=True)

    def get_plant_count(self):
        """Calculate real plant count from claimed plots"""
        try:
            return GardenPlot.query.filter_by(user_id=self.id).filter(
                GardenPlot.status.in_(['mine', 'taken'])
            ).count()
        except:
            return self.plant_count  # Fallback to static field
    
    def get_garden_count(self):
        """Count gardens created by user"""
        try:
            return Garden.query.filter_by(user_id=self.id).count()
        except:
            return 0
    
    def get_following_count(self):
        """Count gardens user is following"""
        try:
            return GardenFollower.query.filter_by(user_id=self.id).count()
        except:
            return 0
    
    def get_followers_count(self):
        """Count users following this user's gardens"""
        try:
            garden_ids = [g.id for g in Garden.query.filter_by(user_id=self.id).all()]
            return GardenFollower.query.filter(GardenFollower.garden_id.in_(garden_ids)).count()
        except:
            return self.friends  # Fallback

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'location': self.location,
            'role': getattr(self, 'role', 'Garden Volunteer'),
            'is_guest': getattr(self, 'is_guest', False),
            'created_at': str(self.created_at) if hasattr(self, 'created_at') and self.created_at else None,
            'last_active': str(self.last_active) if hasattr(self, 'last_active') and self.last_active else None,
            'plant_count': self.get_plant_count(),
            'zone': self.zone,
            'friends': self.friends,
            'streak': self.streak,
            'garden_count': self.get_garden_count(),
            'following_count': self.get_following_count(),
            'followers_count': self.get_followers_count()
        }


class FavoritePlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    user = db.relationship('User', backref='favorite_plants')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    food_type = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    location = db.Column(db.String(200))
    image_url = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    likes = db.Column(db.Integer, default=0)
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


class GardenFollower(db.Model):
    """Model for users following gardens"""
    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey('garden.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    garden = db.relationship('Garden', backref='followers')
    user = db.relationship('User', backref='following_gardens')
    
    # Ensure a user can only follow a garden once
    __table_args__ = (db.UniqueConstraint('garden_id', 'user_id', name='unique_garden_follower'),)


# =========================
#          ROUTES
# =========================

@app.route('/')
def index():
    gardens = Garden.query.all()
    return render_template('index.html', gardens=gardens)


@app.route('/community')
def community():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('community.html', posts=posts)


@app.route('/guest')
def guest_mode():
    """Guest/Kiosk mode - browse-only access"""
    guest_user = User.query.filter_by(username='guest').first()
    if not guest_user:
        # Create guest user if it doesn't exist
        guest_user = User(
            username='guest',
            email='guest@foodshare.local',
            bio='Browse as a guest - kiosk mode',
            location='Community Garden',
            role='Guest',
            is_guest=True
        )
        db.session.add(guest_user)
        db.session.commit()
    
    # Redirect to guest profile
    return profile(guest_user.id)


@app.route('/garden')
def garden():
    gardens = Garden.query.all()
    return render_template('garden.html', gardens=gardens)


# ---------- PROFILE + NEW SECTIONS ----------

@app.route('/profile')
@app.route('/profile/<int:user_id>')
def profile(user_id=1):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).all()
    gardens = Garden.query.filter_by(user_id=user_id).order_by(Garden.timestamp.desc()).all()

    # Calculate real stats
    plant_count = user.get_plant_count()
    following_count = user.get_following_count()
    followers_count = user.get_followers_count()

    favorite_plants = [f.name for f in FavoritePlant.query.filter_by(user_id=user_id).all()]

    # Simple contributions list (computed)
    contributions = [
        f"Created {len(gardens)} garden(s) 🌱",
        f"Shared {len(posts)} community post(s) 🧺",
        "Growing the FoodShare community 🤝"
    ]

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        gardens=gardens,
        plant_count=plant_count,
        following_count=following_count,
        followers_count=followers_count,
        favorite_plants=favorite_plants,
        contributions=contributions
    )


@app.route('/activity')
def activity():
    user_id = 1
    user = User.query.get_or_404(user_id)
    gardens = Garden.query.filter_by(user_id=user_id).order_by(Garden.timestamp.desc()).all()
    return render_template('activity.html', user=user, gardens=gardens)


@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    user_id = 1
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        action = request.form.get('action')
        plant_name = request.form.get('plant_name', '').strip()

        if action == 'add' and plant_name:
            existing = FavoritePlant.query.filter_by(user_id=user_id, name=plant_name).first()
            if not existing:
                db.session.add(FavoritePlant(user_id=user_id, name=plant_name))
                db.session.commit()

        if action == 'remove' and plant_name:
            FavoritePlant.query.filter_by(user_id=user_id, name=plant_name).delete()
            db.session.commit()

        return redirect(url_for('favorites'))

    favorite_plants = [f.name for f in FavoritePlant.query.filter_by(user_id=user_id).all()]
    return render_template('favorites.html', user=user, favorite_plants=favorite_plants)


@app.route('/contributions')
def contributions():
    user_id = 1
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    gardens = Garden.query.filter_by(user_id=user_id).all()

    contributions = [
        f"Created {len(gardens)} garden(s) 🌱",
        f"Shared {len(posts)} community post(s) 🧺",
        "Supports neighbors with surplus produce 💚"
    ]
    return render_template('contributions.html', user=user, contributions=contributions)


# ---------- API: USERS ----------

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


# ---------- API: POSTS ----------

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        food_type = request.form.get('food_type', '')
        quantity = request.form.get('quantity', '')
        location = request.form.get('location', '')
        user_id = int(request.form.get('user_id', 1))

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        request_key = f"post_{user_id}_{title[:50]}"

        with queue_mutex:
            request_queues[request_key].append(request.form.to_dict())
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            post_lock = request_locks[request_key]

        lock_acquired = post_lock.acquire(blocking=False)
        if not lock_acquired:
            post_lock.acquire()
            post_lock.release()

            recent_post = Post.query.filter_by(
                title=title,
                user_id=user_id
            ).order_by(Post.timestamp.desc()).first()

            if recent_post:
                return jsonify(recent_post.to_dict()), 201
            else:
                return jsonify({'error': 'Post creation failed'}), 500

        try:
            time.sleep(0.15)

            with queue_mutex:
                all_requests = request_queues[request_key]
                best_request = all_requests[0] if all_requests else request.form.to_dict()
                request_queues[request_key] = []

            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp_str + filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_filename = filename

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

            return jsonify(post.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            post_lock.release()

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify([p.to_dict() for p in posts])


@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})


@app.route('/api/posts/<int:post_id>/replies', methods=['GET', 'POST'])
def post_replies(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        data = request.json
        content = data.get('content', '').strip()
        user_id = data.get('user_id', 1)

        if not content:
            return jsonify({'error': 'Reply content is required'}), 400

        request_key = f"reply_{post_id}_{user_id}_{content[:50]}"

        with queue_mutex:
            request_queues[request_key].append(data)
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            reply_lock = request_locks[request_key]

        lock_acquired = reply_lock.acquire(blocking=False)
        if not lock_acquired:
            reply_lock.acquire()
            reply_lock.release()

            recent_reply = Reply.query.filter_by(
                post_id=post_id,
                user_id=user_id,
                content=content
            ).order_by(Reply.timestamp.desc()).first()

            if recent_reply:
                return jsonify(recent_reply.to_dict()), 201
            else:
                return jsonify({'error': 'Reply creation failed'}), 500

        try:
            time.sleep(0.15)

            with queue_mutex:
                all_requests = request_queues[request_key]
                best_request = all_requests[-1] if all_requests else data
                request_queues[request_key] = []

            data = best_request
            content = data.get('content', '').strip()
            user_id = data.get('user_id', 1)

            reply = Reply(
                content=content,
                user_id=user_id,
                post_id=post_id
            )
            db.session.add(reply)
            db.session.commit()

            return jsonify(reply.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            reply_lock.release()

    replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.timestamp.asc()).all()
    return jsonify([r.to_dict() for r in replies])


# ---------- API: GARDENS ----------

@app.route('/api/gardens', methods=['GET', 'POST'])
def api_gardens():
    if request.method == 'POST':
        data = request.json
        garden_name = data['name'].strip()

        if not garden_name:
            return jsonify({'error': 'Garden name is required'}), 400

        request_key = garden_name.lower()

        with queue_mutex:
            request_queues[request_key].append(data)
        with locks_mutex:
            if request_key not in request_locks:
                request_locks[request_key] = threading.Lock()
            garden_lock = request_locks[request_key]

        lock_acquired = garden_lock.acquire(blocking=False)
        if not lock_acquired:
            garden_lock.acquire()
            garden_lock.release()

            existing_garden = Garden.query.filter_by(name=garden_name).first()
            if existing_garden:
                return jsonify(existing_garden.to_dict()), 200
            else:
                return jsonify({'error': 'Garden creation failed'}), 500

        try:
            time.sleep(0.15)

            with queue_mutex:
                all_requests = request_queues[request_key]
                best_request = max(all_requests, key=lambda r: len(r.get('plot_states', [])))
                del request_queues[request_key]

            data = best_request

            existing_garden = Garden.query.filter_by(name=garden_name).first()
            if existing_garden:
                return jsonify(existing_garden.to_dict()), 200

            rows = data.get('rows', 5)
            cols = data.get('cols', 5)
            plot_states = data.get('plot_states', [])

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
            return jsonify(garden.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create garden'}), 500
        finally:
            garden_lock.release()
            with locks_mutex:
                if request_key in request_locks:
                    del request_locks[request_key]

    gardens = Garden.query.all()
    return jsonify([g.to_dict() for g in gardens])


@app.route('/api/gardens/<int:garden_id>/plots', methods=['GET'])
def get_garden_plots(garden_id):
    garden = Garden.query.get_or_404(garden_id)
    plots = GardenPlot.query.filter_by(garden_id=garden_id).order_by(GardenPlot.plot_index).all()

    current_user_id = 1
    plots_data = []

    for plot in plots:
        plot_dict = plot.to_dict()
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


# =========================
#        MAIN
# =========================

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        with app.app_context():
            db.create_all()
            if User.query.filter_by(username='demo').first() is None:
                demo_user = User(
                    username='demo',
                    email='demo@foodshare.com',
                    bio='Helping our community grow one plant at a time.',
                    location='Clemson, SC',
                    plant_count=45,
                    zone='Zone 3',
                    friends=18,
                    streak=7
                )
                db.session.add(demo_user)
                db.session.commit()

    app.run(debug=False, port=5000)
