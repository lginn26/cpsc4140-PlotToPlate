#!/usr/bin/env python3
"""
Seed script to populate the FoodShare database with example data for testing.
This creates realistic users, gardens, posts, and community interactions.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Post, Reply, Garden, GardenPlot, GardenFollower

def clear_database():
    """Clear all existing data from the database"""
    print("🗑️  Clearing existing database data...")
    with app.app_context():
        GardenFollower.query.delete()
        Reply.query.delete()
        Post.query.delete()
        GardenPlot.query.delete()
        Garden.query.delete()
        User.query.delete()
        db.session.commit()
    print("✅ Database cleared")

def create_users():
    """Create example users with different roles"""
    print("\n👥 Creating users...")
    
    users_data = [
        {
            'username': 'sarah_gardener',
            'email': 'sarah@example.com',
            'bio': 'Passionate about organic gardening and sustainability. Growing food for 10+ years!',
            'location': 'Downtown Community Garden, Zone 5',
            'role': 'Master Gardener'
        },
        {
            'username': 'mike_green',
            'email': 'mike@example.com',
            'bio': 'New to gardening but excited to learn. Love sharing my tomatoes!',
            'location': 'Northside Gardens, Zone 4',
            'role': 'Community Gardener'
        },
        {
            'username': 'lisa_organics',
            'email': 'lisa@example.com',
            'bio': 'Organic farmer and community garden coordinator. Here to help others grow.',
            'location': 'Clemson Community Farm',
            'role': 'Garden Coordinator'
        },
        {
            'username': 'john_novice',
            'email': 'john@example.com',
            'bio': 'Just started my first garden plot this spring. Learning as I go!',
            'location': 'East Garden',
            'role': 'Garden Volunteer'
        },
        {
            'username': 'emma_harvest',
            'email': 'emma@example.com',
            'bio': 'Growing herbs and vegetables for local food banks. Community first!',
            'location': 'Seneca Gardens',
            'role': 'Community Gardener'
        }
    ]
    
    users = []
    with app.app_context():
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                bio=user_data['bio'],
                location=user_data['location'],
                role=user_data['role'],
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✅ Created {len(users)} users")
    
    return users

def create_gardens(users):
    """Create community gardens"""
    print("\n🌱 Creating gardens...")
    
    gardens_data = [
        {
            'name': 'Tea Garden',
            'description': 'There is a shed in the upper left! Feel free to any other plots!',
            'location': 'Seneca',
            'plants': 'Herbs',
            'rows': 5,
            'cols': 5
        },
        {
            'name': 'seed land',
            'description': 'A diverse garden with vegetables, herbs, and flowers. Perfect for beginners!',
            'location': 'Clemson University',
            'plants': '',
            'rows': 6,
            'cols': 6
        },
        {
            'name': 'Walk way garden',
            'description': 'Linear garden along the community center walkway. Great for herbs and small plants.',
            'location': '',
            'plants': '',
            'rows': 3,
            'cols': 8
        },
        {
            'name': 'dsa',
            'description': 'Experimental plots for testing different growing techniques and companion planting.',
            'location': '',
            'plants': '',
            'rows': 4,
            'cols': 4
        },
        {
            'name': 'y',
            'description': '',
            'location': '',
            'plants': '',
            'rows': 7,
            'cols': 7
        }
    ]
    
    gardens = []
    with app.app_context():
        for i, garden_data in enumerate(gardens_data):
            # Assign garden to a user
            user = users[i % len(users)]
            
            garden = Garden(
                name=garden_data['name'],
                description=garden_data['description'],
                location=garden_data['location'],
                plants=garden_data['plants'],
                user_id=user.id,
                rows=garden_data['rows'],
                cols=garden_data['cols'],
                timestamp=datetime.utcnow() - timedelta(days=random.randint(10, 180))
            )
            db.session.add(garden)
            gardens.append(garden)
        
        db.session.commit()
        print(f"✅ Created {len(gardens)} gardens")
    
    return gardens

def create_garden_plots(gardens, users):
    """Create plots for each garden with various statuses"""
    print("\n📍 Creating garden plots...")
    
    plot_count = 0
    with app.app_context():
        for garden in gardens:
            total_plots = garden.rows * garden.cols
            
            # Create some special plots (water, tools)
            water_plots = random.sample(range(total_plots), k=min(2, total_plots // 10))
            tool_plots = random.sample([i for i in range(total_plots) if i not in water_plots], k=min(1, total_plots // 15))
            
            for plot_index in range(total_plots):
                # Determine plot status
                if plot_index in water_plots:
                    status = 'water'
                    user_id = None
                elif plot_index in tool_plots:
                    status = 'tools'
                    user_id = None
                elif random.random() < 0.3:  # 30% claimed
                    status = random.choice(['mine', 'taken'])
                    user_id = random.choice(users).id
                elif random.random() < 0.6:  # 60% available
                    status = 'available'
                    user_id = None
                else:  # 10% unavailable
                    status = 'null'
                    user_id = None
                
                plot = GardenPlot(
                    garden_id=garden.id,
                    plot_index=plot_index,
                    status=status,
                    user_id=user_id,
                    claimed_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)) if user_id else None,
                    water_available=random.choice([True, False]),
                    tools_available=random.choice([True, False]),
                    soil_type=random.choice(['loam', 'clay', 'sandy', 'silt']),
                    sunlight_level=random.choice(['full sun', 'partial shade', 'full shade']),
                    notes='Great spot for tomatoes!' if random.random() < 0.2 else None
                )
                db.session.add(plot)
                plot_count += 1
        
        db.session.commit()
        print(f"✅ Created {plot_count} garden plots")

def create_posts(users):
    """Create community posts"""
    print("\n📝 Creating community posts...")
    
    posts_data = [
        {
            'title': 'Fresh Tomatoes Available!',
            'content': 'I have an abundance of cherry tomatoes from my garden. Free to anyone who wants them! They are organic and super sweet.',
            'food_type': 'Tomatoes',
            'quantity': '5 lbs',
            'location': 'Downtown Garden'
        },
        {
            'title': 'Looking for Herb Cuttings',
            'content': 'Does anyone have basil or mint cuttings they could share? I am starting my herb garden and would love some starter plants.',
            'food_type': 'Herbs',
            'quantity': 'A few cuttings',
            'location': 'Northside'
        },
        {
            'title': 'Zucchini Overload - Come Get Some!',
            'content': 'My zucchini plants have produced way more than I can use. Please come take some off my hands before they get too big! Located near plot #15.',
            'food_type': 'Zucchini',
            'quantity': '10+ zucchinis',
            'location': 'Community Garden'
        },
        {
            'title': 'Gardening Workshop This Saturday',
            'content': 'Join us for a free workshop on composting and soil health! Bring your questions and we will have refreshments. 10 AM at the main shed.',
            'food_type': '',
            'quantity': '',
            'location': 'Tea Garden Shed'
        },
        {
            'title': 'Free Lettuce Seeds',
            'content': 'I bought too many lettuce seed packets. Happy to share with anyone who wants to plant some fall greens!',
            'food_type': 'Seeds',
            'quantity': '5 packets',
            'location': 'East Garden'
        },
        {
            'title': 'Need Help with Pest Control',
            'content': 'My pepper plants are being attacked by aphids. Does anyone have organic pest control tips? I would prefer not to use chemicals.',
            'food_type': '',
            'quantity': '',
            'location': 'Plot 23'
        },
        {
            'title': 'Sharing Fresh Herbs',
            'content': 'Oregano, thyme, and rosemary ready for harvest. Stop by anytime to clip what you need!',
            'food_type': 'Herbs',
            'quantity': 'Plenty',
            'location': 'Herb Corner'
        },
        {
            'title': 'Pumpkins Ready for Halloween!',
            'content': 'Grew some decorative pumpkins perfect for fall decorations. Free for the taking!',
            'food_type': 'Pumpkins',
            'quantity': '8 pumpkins',
            'location': 'Seneca Gardens'
        }
    ]
    
    posts = []
    with app.app_context():
        for post_data in posts_data:
            user = random.choice(users)
            
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                food_type=post_data['food_type'],
                quantity=post_data['quantity'],
                location=post_data['location'],
                user_id=user.id,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                likes=random.randint(0, 25),
                status=random.choice(['active', 'active', 'active', 'resolved'])  # Mostly active
            )
            db.session.add(post)
            posts.append(post)
        
        db.session.commit()
        print(f"✅ Created {len(posts)} posts")
    
    return posts

def create_replies(posts, users):
    """Create replies to posts"""
    print("\n💬 Creating replies...")
    
    replies_data = [
        "Thanks for sharing! I'll stop by later today.",
        "Do you still have some available?",
        "This is so generous of you! Thank you!",
        "I'd love to take some. When is the best time?",
        "Great idea! Count me in.",
        "I have some tips that might help with that.",
        "Would you be willing to trade for some of my carrots?",
        "I'm interested! Can I pick up tomorrow?",
        "This community is amazing! Thanks for doing this.",
        "I tried the same thing last year and had great success.",
        "Let me know if you need any help!",
        "Perfect timing! I was just looking for this."
    ]
    
    reply_count = 0
    with app.app_context():
        for post in posts:
            # Each post gets 0-5 replies
            num_replies = random.randint(0, 5)
            
            for _ in range(num_replies):
                user = random.choice([u for u in users if u.id != post.user_id])
                
                reply = Reply(
                    content=random.choice(replies_data),
                    user_id=user.id,
                    post_id=post.id,
                    timestamp=post.timestamp + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(reply)
                reply_count += 1
        
        db.session.commit()
        print(f"✅ Created {reply_count} replies")

def create_garden_followers(gardens, users):
    """Create garden following relationships"""
    print("\n❤️  Creating garden followers...")
    
    follower_count = 0
    with app.app_context():
        for user in users:
            # Each user follows 1-3 gardens
            num_to_follow = random.randint(1, 3)
            gardens_to_follow = random.sample([g for g in gardens if g.user_id != user.id], k=min(num_to_follow, len(gardens) - 1))
            
            for garden in gardens_to_follow:
                follower = GardenFollower(
                    garden_id=garden.id,
                    user_id=user.id,
                    followed_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
                )
                db.session.add(follower)
                follower_count += 1
        
        db.session.commit()
        print(f"✅ Created {follower_count} garden followers")

def main():
    """Main function to seed the database"""
    print("=" * 60)
    print("🌱 FoodShare Database Seeding Script")
    print("=" * 60)
    
    # Clear existing data
    clear_database()
    
    # Create all data
    users = create_users()
    gardens = create_gardens(users)
    create_garden_plots(gardens, users)
    posts = create_posts(users)
    create_replies(posts, users)
    create_garden_followers(gardens, users)
    
    print("\n" + "=" * 60)
    print("✅ Database seeding completed successfully!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   • {len(users)} users created")
    print(f"   • {len(gardens)} gardens created")
    print(f"   • {len(posts)} posts created")
    print(f"   • Community interactions added")
    print("\n🎉 You can now test the FoodShare application with realistic data!")

if __name__ == '__main__':
    main()
