================================================================================
                    FOODSHARE APPLICATION SETUP GUIDE
================================================================================

PROJECT: FoodShare - Community Food Sharing Platform
COURSE: CPSC 6140
TEAM: 4, Polymorphs



Quick Start:
  1. make setup
  2. make run
  3. Open browser to http://localhost:5000






=================================================
or


Step 1: Navigate to the project directory
    cd /path/to/cpsc4140-PlotToPlate

Step 2: Verify you're in the correct directory
    ls -la
    
    You should see:
    - foodshare-app/ directory
    - Makefile
    - README.md
    - README.txt (this file)

Run the following single command to set up everything:

    make setup

This will:
- Create a Python virtual environment
- Install all required dependencies
- Set up the database with initial tables


From the project root directory, run:

    make run

Expected output:
    Starting FoodShare application...
    * Serving Flask app 'app'
    * Debug mode: off
    * Running on http://127.0.0.1:5000


Navigate the application

    Available Pages:
    ----------------
    Home        : http://localhost:5000/
    Community   : http://localhost:5000/community
    Gardens     : http://localhost:5000/garden
    Profile     : http://localhost:5000/profile