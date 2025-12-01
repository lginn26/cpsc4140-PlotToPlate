# FoodShare Deployment Guide 🚀

## Option 1: Render.com (Recommended - Free Tier Available)

**✅ Easiest deployment with free tier**

### Steps:
1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add production deployment files"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `lginn26/cpsc4140-PlotToPlate`
   - Configure:
     - **Name**: `foodshare-app`
     - **Environment**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `cd foodshare-app && gunicorn --bind 0.0.0.0:$PORT wsgi:app`
   - Click "Create Web Service"

3. **Environment Variables** (in Render dashboard):
   - `SECRET_KEY`: Generate random string (important for security)
   - `SEED_DATABASE`: `true` (to populate with example data)

### Result:
- **Live URL**: `https://foodshare-app.onrender.com` (or similar)
- **Free tier**: 750 hours/month (sleeps after 15min inactive)
- **Automatic deploys**: Updates when you push to GitHub

---

## Option 2: Railway.app

**✅ Good alternative with $5/month hobby tier**

### Steps:
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Deploy automatically uses our `Procfile`

---

## Option 3: PythonAnywhere (Free Tier)

**✅ Great for beginners**

### Steps:
1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. Upload files to `/home/yourusername/foodshare/`
3. Create web app with manual configuration
4. Set WSGI file to point to your `wsgi.py`

---

## Option 4: DigitalOcean App Platform

**💰 $5/month minimum**

### Steps:
1. Connect to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Import from GitHub
3. Uses our `Procfile` automatically

---

## Local Production Testing

Test production setup locally:

```bash
# Install production dependencies
pip install -r foodshare-app/requirements.txt

# Run with gunicorn
cd foodshare-app
gunicorn --bind 127.0.0.1:8000 wsgi:app
```

Visit: http://127.0.0.1:8000

---

## Production Features

✅ **Gunicorn WSGI server** (production-ready)  
✅ **Environment configuration** (secrets via env vars)  
✅ **Automatic database setup** (migrations in build script)  
✅ **Example data seeding** (optional via SEED_DATABASE env var)  
✅ **File upload handling** (static directory creation)  
✅ **Security headers** (SECRET_KEY configuration)

---

## Next Steps After Deployment

1. **Custom Domain** (optional): Configure in your hosting provider
2. **SSL Certificate**: Usually automatic on modern platforms
3. **Database Backups**: Set up regular backups of SQLite file
4. **Monitoring**: Use hosting platform's built-in monitoring
5. **Updates**: Push to GitHub → automatic deployment

## Recommended: Start with Render.com

**Free tier, easy setup, automatic deploys from GitHub!**