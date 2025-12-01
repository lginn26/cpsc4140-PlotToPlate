# FoodShare Database Seeding

This directory contains scripts and assets to populate the FoodShare database with realistic example data for testing and demonstration purposes.

## Quick Start

1. **Run the seed script:**
   ```bash
   cd foodshare-app/seed_data
   python3 seed_database.py
   ```

2. **The script will:**
   - Clear existing database data
   - Create 5 example users with different roles
   - Create 5 community gardens with various layouts
   - Generate garden plots (available, claimed, water sources, tool hubs)
   - Create 8 community posts about food sharing
   - Add replies to posts
   - Create following relationships between users and gardens

## What Gets Created

### Users (5)
- **sarah_gardener** - Master Gardener with 10+ years experience
- **mike_green** - Community Gardener, loves tomatoes
- **lisa_organics** - Garden Coordinator, organic farmer
- **john_novice** - Garden Volunteer, beginner
- **emma_harvest** - Community Gardener, grows for food banks

### Gardens (5)
- **Tea Garden** - 5x5 grid in Seneca with shed
- **seed land** - 6x6 grid at Clemson University
- **Walk way garden** - 3x8 linear layout
- **dsa** - 4x4 experimental plots
- **y** - 7x7 large garden

### Posts (8)
- Fresh produce sharing (tomatoes, zucchini, herbs)
- Workshop announcements
- Seed sharing
- Gardening help requests
- Seasonal items (pumpkins)

### Garden Plots
Each garden contains plots with various statuses:
- **Available** - Green plots ready to claim
- **Claimed** - Plots assigned to users
- **Water sources** - Blue plots with water droplet icons
- **Tool hubs** - Orange plots with wrench icons
- **Unavailable** - Gray plots not for planting

## Directory Structure

```
seed_data/
├── README.md              # This file
├── seed_database.py       # Main seeding script
├── images/                # (Optional) Header photos for posts
│   ├── tomatoes.jpg
│   ├── herbs.jpg
│   ├── zucchini.jpg
│   └── pumpkins.jpg
└── sample_data/           # (Optional) Additional data files
    └── plants.json        # Plant varieties and info
```

## Adding Images

To add header photos for posts:

1. Place images in the `images/` folder
2. Name them descriptively (e.g., `fresh_tomatoes.jpg`)
3. Update the seed script to reference images:

```python
post = Post(
    title='Fresh Tomatoes Available!',
    content='...',
    image_url='/static/uploads/tomatoes.jpg',
    ...
)
```

## Customization

### Adding More Users

Edit `create_users()` in `seed_database.py`:

```python
users_data = [
    {
        'username': 'your_username',
        'email': 'your@email.com',
        'bio': 'Your bio text',
        'location': 'Your location',
        'role': 'Garden Volunteer'  # or Master Gardener, etc.
    },
    # ... more users
]
```

### Adding More Gardens

Edit `create_gardens()` in `seed_database.py`:

```python
gardens_data = [
    {
        'name': 'My Garden',
        'description': 'Description here',
        'location': 'Location',
        'plants': 'Plant types',
        'rows': 5,
        'cols': 5
    },
    # ... more gardens
]
```

### Adding More Posts

Edit `create_posts()` in `seed_database.py`:

```python
posts_data = [
    {
        'title': 'Post Title',
        'content': 'Post content here',
        'food_type': 'Food type',
        'quantity': 'Amount',
        'location': 'Location'
    },
    # ... more posts
]
```

## Resetting the Database

To start fresh, just run the script again:

```bash
python3 seed_database.py
```

The script will automatically:
1. Delete all existing data
2. Recreate everything from scratch

## Testing Scenarios

After seeding, you can test:

### Profile Features
- Visit `/profile` to see user stats
- Check plant count (from claimed plots)
- View follower counts
- See created gardens and posts

### Garden Features
- Visit `/garden` to browse all gardens
- Click "View Plots" to see garden layouts
- Test plot claiming/releasing
- Follow/unfollow gardens

### Community Features
- Visit `/community` to see posts
- Like posts
- Add replies to posts
- Mark posts as resolved
- Delete your own posts

### Guest Mode
- Visit `/guest` to browse in kiosk mode
- Verify guest user can't edit profiles

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the correct directory:
```bash
cd /path/to/foodshare-app/seed_data
python3 seed_database.py
```

### Database Locked
If the database is locked, stop the Flask app first:
```bash
pkill -f "python3 app.py"
python3 seed_database.py
```

### Missing Dependencies
Ensure Flask and SQLAlchemy are installed:
```bash
pip3 install -r requirements.txt
```

## Production Notes

⚠️ **WARNING**: This script is for **development and testing only**!

- Never run this on a production database
- It will delete all existing data
- Use proper database migrations in production
- Backup your data before running

## Contributing

To add more realistic data:
1. Edit the seed script
2. Add diverse user profiles
3. Include variety in garden layouts
4. Create engaging post content
5. Test thoroughly before committing

## License

Part of the FoodShare application for CPSC 6140/4140.
