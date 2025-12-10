#!/usr/bin/env python3
"""
Seed script to populate the FoodShare database with example data for testing.
This creates realistic users, gardens, posts, and community interactions.
"""
import sys
import os
import shutil
from datetime import datetime, timedelta
import random

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Post, Reply, Garden, GardenPlot, GardenFollower

def copy_seed_images():
    """Copy images from seed_data/images to static/uploads"""
    print("📷 Copying seed images to uploads folder...")
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_source = os.path.join(script_dir, 'images')
    app_dir = os.path.dirname(script_dir)
    uploads_dest = os.path.join(app_dir, 'static', 'uploads')
    
    # Create uploads directory if it doesn't exist
    os.makedirs(uploads_dest, exist_ok=True)
    
    # Copy images if source directory exists
    if os.path.exists(images_source):
        for filename in os.listdir(images_source):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                source_path = os.path.join(images_source, filename)
                dest_path = os.path.join(uploads_dest, filename)
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"  ✅ Copied {filename}")
                except Exception as e:
                    print(f"  ❌ Failed to copy {filename}: {e}")
    else:
        print("  ⚠️  Images source directory not found")

def clear_database():
    """Clear all existing data from the database"""
    print("🗑️  Clearing existing database data...")
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
            'name': 'Heritage Herb Haven',
            'description': 'A medicinal and culinary herb garden featuring heirloom varieties passed down through generations. Includes a greenhouse and tool shed in the northeast corner.',
            'location': 'Downtown Community Center',
            'plants': 'Basil, Rosemary, Thyme, Sage, Lavender, Mint',
            'rows': 5,
            'cols': 6
        },
        {
            'name': 'Victory Garden Collective',
            'description': 'Inspired by WWII victory gardens, this space focuses on high-yield vegetables and food security. Features raised beds and rainwater collection system.',
            'location': 'Clemson University Campus',
            'plants': 'Tomatoes, Beans, Squash, Corn, Carrots, Onions',
            'rows': 7,
            'cols': 8
        },
        {
            'name': 'Pollinator Paradise',
            'description': 'A native plant sanctuary designed to support local bees, butterflies, and birds. Combines food production with habitat restoration.',
            'location': 'Riverside Park',
            'plants': 'Sunflowers, Wildflowers, Berry Bushes, Native Herbs',
            'rows': 4,
            'cols': 5
        },
        {
            'name': 'Vertical Growing Lab',
            'description': 'Experimental vertical farming space exploring space-efficient growing methods. Features towers, trellises, and hydroponic systems.',
            'location': 'Innovation District',
            'plants': 'Lettuce, Spinach, Climbing Peas, Cucumbers',
            'rows': 3,
            'cols': 4
        },
        {
            'name': 'Cultural Fusion Garden',
            'description': 'Celebrating diverse food traditions with plots dedicated to different cultural cuisines from around the world.',
            'location': 'Multicultural Center',
            'plants': 'Hot Peppers, Asian Greens, Mediterranean Herbs, Latin Vegetables',
            'rows': 6,
            'cols': 7
        },
        {
            'name': 'Kids Discovery Garden',
            'description': 'Child-friendly garden with easy-to-grow plants and educational signage. Perfect for school groups and families.',
            'location': 'Elementary School',
            'plants': 'Cherry Tomatoes, Radishes, Sunflowers, Strawberries',
            'rows': 4,
            'cols': 4
        }
    ]
    
    gardens = []
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
                    claimed_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)) if user_id else None
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
            'title': '🍅 Heirloom Tomatoes - Peak Season!',
            'content': 'My Cherokee Purple and Brandywine tomatoes are at their absolute best right now! These heirloom varieties have incredible flavor - nothing like store-bought. Perfect for fresh salads, sandwiches, or sauce. Come by plot #12 in Victory Garden Collective.',
            'food_type': 'Heirloom Tomatoes',
            'quantity': '15-20 large tomatoes',
            'location': 'Victory Garden Collective - Plot 12',
            'image_url': 'Tomato-header.png'
        },
        {
            'title': '🌿 Fresh Herb Starter Kit Available',
            'content': 'I\'ve propagated way too many herb cuttings! Perfect timing for fall planting. Includes: organic basil, rosemary, thyme, oregano, and sage. All grown without pesticides in our Heritage Herb Haven. Great for beginners or expanding your herb collection.',
            'food_type': 'Herb Cuttings & Plants',
            'quantity': '5 starter pots per person',
            'location': 'Heritage Herb Haven - Main Shed',
            'image_url': 'herb-header.jpg'
        },
        {
            'title': '🥒 Cucumber & Pickling Cucumber Bonanza',
            'content': 'Our vertical cucumber towers are producing like crazy! I have both slicing cucumbers and perfect pickling cukes. Also sharing my grandmother\'s pickle recipe if anyone\'s interested. First come, first served!',
            'food_type': 'Cucumbers',
            'quantity': '3-4 bags full',
            'location': 'Vertical Growing Lab'
        },
        {
            'title': '🌻 Sunflower Seeds & Fall Planting Workshop',
            'content': 'Harvested hundreds of sunflower seeds from our Pollinator Paradise garden! Join us Saturday 10 AM for a seed saving workshop. We\'ll cover how to properly dry, store, and plant seeds for next year. Hot cider and fresh bread included!',
            'food_type': 'Sunflower Seeds & Workshop',
            'quantity': 'Seeds for 20+ people',
            'location': 'Pollinator Paradise - Education Pavilion'
        },
        {
            'title': '🌶️ International Hot Pepper Exchange',
            'content': 'Our Cultural Fusion Garden has produced an amazing variety of peppers from around the world! Thai chilies, Hungarian wax peppers, Mexican jalapeños, and Korean gochugaru peppers. Let\'s trade recipes too!',
            'food_type': 'International Hot Peppers',
            'quantity': 'Mixed varieties, 2-3 peppers each type',
            'location': 'Cultural Fusion Garden'
        },
        {
            'title': '🥬 Asian Greens Harvest - Perfect for Stir-Fry',
            'content': 'Bok choy, napa cabbage, and mizuna are ready! These cool-weather crops are at their peak tenderness. Perfect timing for cozy fall cooking. Also have some ginger and green onions to go with them.',
            'food_type': 'Asian Greens & Aromatics',
            'quantity': 'Enough for 8-10 stir-fry meals',
            'location': 'Cultural Fusion Garden'
        },
        {
            'title': '🍓 Late Season Strawberries & Garden Tour',
            'content': 'Our Kids Discovery Garden has a surprise second harvest of strawberries! Bring the little ones for a garden tour and berry picking. We\'ll also have seed packets and coloring books about plants.',
            'food_type': 'Strawberries',
            'quantity': '2-3 cups of berries',
            'location': 'Kids Discovery Garden'
        },
        {
            'title': '🥕 Rainbow Carrots & Root Vegetable Medley',
            'content': 'Just pulled the most beautiful rainbow carrots - purple, orange, yellow, and white! Also have parsnips and turnips. These storage crops will keep well and are perfect for roasting or winter soups.',
            'food_type': 'Root Vegetables',
            'quantity': '5 lbs mixed roots',
            'location': 'Victory Garden Collective'
        },
        {
            'title': '🧄 Garlic Planting & Bulk Herb Tea Blend',
            'content': 'It\'s garlic planting season! I have certified organic seed garlic (hardneck and softneck varieties). Also blended a large batch of our signature relaxation tea using herbs from our garden - chamomile, lemon balm, and lavender.',
            'food_type': 'Seed Garlic & Herbal Tea',
            'quantity': '20 garlic bulbs, 1 cup tea blend',
            'location': 'Heritage Herb Haven'
        },
        {
            'title': '🌽 Sweet Corn & Three Sisters Harvest',
            'content': 'Our traditional Three Sisters planting (corn, beans, squash) is ready for harvest! This sustainable growing method produces amazing flavors. Perfect for a fall feast. Come learn about indigenous growing techniques too!',
            'food_type': 'Corn, Beans & Winter Squash',
            'quantity': '10 ears corn, 2 lbs beans, 3 small squash',
            'location': 'Victory Garden Collective - Traditional Section'
        },
        {
            'title': '💐 Edible Flowers & Pollinator Plant Seeds',
            'content': 'Our pollinator garden has gorgeous edible flowers - nasturtiums, calendula, and bee balm. Perfect for salads and teas. Also collected seeds from our native wildflowers to share for next year\'s plantings.',
            'food_type': 'Edible Flowers & Native Seeds',
            'quantity': 'Fresh flowers + seed packets',
            'location': 'Pollinator Paradise'
        },
        {
            'title': '🥗 Microgreens & Hydroponic Lettuce Demo',
            'content': 'Our vertical farming experiment is producing incredible microgreens and butter lettuce! Come see our hydroponic setup in action. Perfect opportunity to learn about soil-free growing methods for small spaces.',
            'food_type': 'Microgreens & Hydroponic Lettuce',
            'quantity': 'Mixed microgreen trays, 6 lettuce heads',
            'location': 'Vertical Growing Lab - Hydroponic Station'
        }
    ]
    
    posts = []
    for post_data in posts_data:
        user = random.choice(users)
        
        post = Post(
            title=post_data['title'],
            content=post_data['content'],
            food_type=post_data['food_type'],
            quantity=post_data['quantity'],
            location=post_data['location'],
            image_url=post_data.get('image_url'),
            user_id=user.id,
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            likes=random.randint(0, 25)
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
    
    # Copy seed images first
    copy_seed_images()
    
    with app.app_context():
        # Clear existing data
        clear_database()
        
        # Create all data in single context
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
    print(f"   • Seed images copied to uploads")
    print("\n🎉 You can now test the FoodShare application with realistic data!")

if __name__ == '__main__':
    main()
