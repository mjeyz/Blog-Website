# The Insight Hub - Blog Platform

The Insight Hub is a modern blog platform designed to share knowledge, creativity, and perspectives across technology, lifestyle, and innovation. Built with Flask and PostgreSQL, it allows users to register, publish, and engage through insightful posts and comments.

## Features

- 🔐 User Authentication & Authorization
- 📝 Create, Edit & Delete Posts (Admin)
- 💬 Comment System
- 👤 User Profiles with Follow/Unfollow
- 🖼️ Profile Picture Upload
- 📱 Responsive Design
- 🛡️ Admin Dashboard
- 🔒 Password Management

## Tech Stack

- **Backend:** Python/Flask
- **Database:** PostgreSQL
- **Frontend:** HTML/CSS, Bootstrap 5
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF
- **Editor:** CKEditor
- **Server:** Gunicorn

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mjeyz/Blog-Website.git
cd Blog-Website
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
```bash
cp .env.example .env
```

5. Configure your PostgreSQL database:
   - Create a database named `blog_db` (or your preferred name)
   - Update `.env` with your database credentials

6. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Deployment

This application is ready to be deployed on various platforms. Below are instructions for popular hosting services:

### Deploy to Heroku

1. Create a Heroku account at [heroku.com](https://heroku.com)

2. Install the Heroku CLI:
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

3. Login to Heroku:
```bash
heroku login
```

4. Create a new Heroku app:
```bash
heroku create your-app-name
```

5. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:essential-0
```

6. Set environment variables:
```bash
heroku config:set FLASK_KEY=your-secret-key-here
```

7. Deploy your code:
```bash
git push heroku main
```

8. Initialize the database (it will auto-initialize on first run)

9. Open your app:
```bash
heroku open
```

### Deploy to Railway

1. Sign up at [railway.app](https://railway.app)

2. Install Railway CLI:
```bash
npm i -g @railway/cli
```

3. Login to Railway:
```bash
railway login
```

4. Initialize and deploy:
```bash
railway init
railway up
```

5. Add PostgreSQL database:
   - Go to your Railway project dashboard
   - Click "New" → "Database" → "PostgreSQL"

6. Set environment variables:
   - Go to your service settings
   - Add `FLASK_KEY` variable

7. Your app will be automatically deployed

### Deploy to Render

1. Sign up at [render.com](https://render.com)

2. Create a new Web Service:
   - Connect your GitHub repository
   - Select "Python" environment
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`

3. Add PostgreSQL database:
   - Go to Dashboard → New → PostgreSQL
   - Connect it to your web service

4. Add environment variables in the Render dashboard:
   - `FLASK_KEY`: Your secret key
   - Database variables will be auto-configured

5. Deploy!

### Environment Variables

Required environment variables for deployment:

- `FLASK_KEY`: Secret key for Flask sessions (generate a strong random key)
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port (default: 5432)

Note: Some platforms (like Heroku) provide a single `DATABASE_URL` instead of individual variables.

## Project Structure

```
Blog-Website/
├── main.py              # Main Flask application
├── database.py          # Database initialization and configuration
├── forms.py             # WTForms form definitions
├── functions.py         # Utility functions (image processing)
├── requirements.txt     # Python dependencies
├── Procfile            # Heroku deployment configuration
├── runtime.txt         # Python version specification
├── .env.example        # Example environment variables
├── static/             # Static files (CSS, JS, images)
│   ├── assets/
│   ├── css/
│   └── profile_pics/   # User uploaded profile pictures
└── templates/          # HTML templates
    ├── index.html
    ├── post.html
    ├── profile.html
    └── ...
```

## First Admin User

The first user to register (user with ID = 1) will automatically become an admin with privileges to:
- Create new posts
- Edit any post
- Delete any post

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
