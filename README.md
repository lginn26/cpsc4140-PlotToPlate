# FoodShare

A community platform for sharing surplus food and managing community gardens.

## Quick Start

```bash
make setup    # Install dependencies & setup database
make run      # Start application at http://localhost:5000
```

**Or manually:**
```bash
cd foodshare-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 migrate_add_replies.py
python3 app.py
```

## Features

- **Community Forum**: Share surplus food, like posts, reply to posts
- **Garden Management**: Create gardens, claim/release plots
- **User Profiles**: Track your gardens and posts
- **Accessibility**: Skip links, keyboard navigation, mobile responsive

## Tech Stack

**Backend**: Flask, SQLAlchemy, SQLite  
**Frontend**: Bootstrap 5, JavaScript, Font Awesome

## Database

- **User**: Accounts and profiles
- **Post**: Food donations with likes
- **Reply**: Comments on posts
- **Garden**: Community gardens
- **GardenPlot**: Individual garden plots

## Project Structure

```
foodshare-app/
├── app.py                    # Flask app & routes
├── requirements.txt          # Dependencies
├── migrate_add_replies.py    # Database migration
├── database/foodshare.db     # SQLite database
├── static/                   # CSS, JS, images
└── templates/                # HTML templates
```

## Documentation

See **README.txt** for detailed setup instructions for Linux systems.
