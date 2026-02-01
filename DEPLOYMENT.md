# Deployment Guide

This guide provides detailed instructions for deploying The Insight Hub blog platform to various cloud hosting services.

## Table of Contents

- [Quick Deploy Options](#quick-deploy-options)
- [Heroku Deployment](#heroku-deployment)
- [Railway Deployment](#railway-deployment)
- [Render Deployment](#render-deployment)
- [Environment Variables](#environment-variables)
- [Post-Deployment Steps](#post-deployment-steps)

## Quick Deploy Options

### Deploy to Heroku (One-Click)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Click the button above to deploy directly to Heroku. The `app.json` file will automatically configure your application.

## Heroku Deployment

### Prerequisites
- A Heroku account ([sign up here](https://signup.heroku.com/))
- Heroku CLI installed ([installation guide](https://devcenter.heroku.com/articles/heroku-cli))
- Git installed

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**
   ```bash
   heroku create your-blog-name
   ```
   Replace `your-blog-name` with your desired app name (must be unique across Heroku).

3. **Add PostgreSQL database**
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```
   
   This automatically sets the `DATABASE_URL` environment variable.

4. **Set environment variables**
   ```bash
   heroku config:set FLASK_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
   ```

5. **Deploy your code**
   ```bash
   git push heroku main
   ```
   
   Or if you're on a different branch:
   ```bash
   git push heroku your-branch:main
   ```

6. **Open your application**
   ```bash
   heroku open
   ```

### Monitoring and Logs

- View logs: `heroku logs --tail`
- Open dashboard: `heroku open --app your-app-name`
- Check database: `heroku pg:info`

## Railway Deployment

### Prerequisites
- A Railway account ([sign up here](https://railway.app))
- Railway CLI (optional, but recommended)

### Method 1: Deploy via GitHub (Recommended)

1. **Fork/Push to GitHub**
   - Ensure your code is in a GitHub repository

2. **Create New Project on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL Database**
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically connect it to your service

4. **Configure Environment Variables**
   - Click on your service
   - Go to "Variables" tab
   - Add `FLASK_KEY` with a strong random value:
     ```
     FLASK_KEY=your-secret-key-here
     ```

5. **Deploy**
   - Railway will automatically deploy your application
   - You'll get a public URL (e.g., `your-app.up.railway.app`)

### Method 2: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and deploy**
   ```bash
   railway init
   railway up
   ```

4. **Add PostgreSQL**
   ```bash
   railway add postgresql
   ```

5. **Set environment variables**
   ```bash
   railway variables set FLASK_KEY=your-secret-key-here
   ```

## Render Deployment

### Prerequisites
- A Render account ([sign up here](https://render.com))
- Your code in a GitHub repository

### Steps

1. **Create a New Web Service**
   - Log in to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

2. **Configure the Service**
   - **Name**: Choose a name for your service
   - **Environment**: `Python`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     gunicorn main:app
     ```
   - **Instance Type**: Free (or choose a paid plan)

3. **Add PostgreSQL Database**
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Give it a name (e.g., `blog-database`)
   - Choose a region and plan
   - Click "Create Database"
   - Once created, copy the "Internal Database URL"

4. **Set Environment Variables**
   - Go back to your web service
   - Click "Environment" in the sidebar
   - Add the following variables:
     ```
     FLASK_KEY=your-secret-key-here
     DATABASE_URL=<paste-your-internal-database-url>
     ```

5. **Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Or wait for automatic deployment (if connected to GitHub)

6. **Access Your App**
   - Your app will be available at `https://your-service-name.onrender.com`

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_KEY` | Secret key for Flask sessions | `your-secret-key-here` |

### Database Configuration

**Option 1: Single DATABASE_URL (Recommended for cloud platforms)**
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |

**Option 2: Individual variables (For custom setups)**
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_NAME` | Database name | `postgres` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | - |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

### Generating a Secure Flask Key

Use one of these methods to generate a secure key:

**Python:**
```bash
python -c 'import secrets; print(secrets.token_hex(16))'
```

**OpenSSL:**
```bash
openssl rand -hex 32
```

## Post-Deployment Steps

### 1. Create Your First Admin User

The first user to register (ID = 1) will automatically become an admin.

1. Navigate to your deployed application
2. Click "Register"
3. Create your account
4. You now have admin privileges to:
   - Create new posts
   - Edit any post
   - Delete any post

### 2. Customize Your Blog

After deployment, you may want to:
- Update the blog title in templates
- Add your own logo to `static/assets/img/`
- Customize styles in `static/css/styles.css`
- Update the About page content

### 3. Set Up Custom Domain (Optional)

#### Heroku
```bash
heroku domains:add www.yourdomain.com
```
Then configure your DNS provider with the provided DNS target.

#### Railway
- Go to your service settings
- Click "Settings" → "Domains"
- Add your custom domain
- Update your DNS records as instructed

#### Render
- Go to your service "Settings"
- Scroll to "Custom Domains"
- Add your domain and follow DNS configuration instructions

## Troubleshooting

### Common Issues

**Application Error on Startup**
- Check logs: `heroku logs --tail` (Heroku) or view logs in dashboard
- Ensure `DATABASE_URL` or database variables are set correctly
- Verify `FLASK_KEY` is set

**Database Connection Error**
- Confirm PostgreSQL addon/database is provisioned
- Check that `DATABASE_URL` is set correctly
- Verify database credentials

**Static Files Not Loading**
- Ensure `static/` folder is committed to git
- Check that files exist in the deployment

**Module Import Errors**
- Verify all dependencies are in `requirements.txt`
- Try re-deploying with fresh build

### Getting Help

- **Heroku**: Check [Heroku Dev Center](https://devcenter.heroku.com/)
- **Railway**: Visit [Railway Docs](https://docs.railway.app/)
- **Render**: See [Render Guides](https://render.com/docs)
- **GitHub Issues**: Open an issue on the repository

## Database Management

### Backup Your Database

**Heroku:**
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

**Railway/Render:**
Use the platform's dashboard to create backups or use `pg_dump`:
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore a Backup

**Heroku:**
```bash
heroku pg:backups:restore [BACKUP_ID]
```

### Reset Database

**Warning: This will delete all data!**

**Heroku:**
```bash
heroku pg:reset DATABASE_URL
heroku run python -c "from database import init_postgres_db; init_postgres_db()"
```

## Security Recommendations

1. **Never commit `.env` file** - It's in `.gitignore` by default
2. **Use strong random keys** for `FLASK_KEY`
3. **Enable HTTPS** - All platforms provide free SSL certificates
4. **Regularly update dependencies**: `pip list --outdated`
5. **Set up monitoring** and error tracking
6. **Regular backups** of your database

## Performance Optimization

1. **Use a CDN** for static files in production
2. **Enable caching** for static assets
3. **Optimize images** in the `static/` folder
4. **Use connection pooling** for database (consider using `SQLAlchemy` with connection pooling)
5. **Monitor application performance** using platform tools

## Scaling

As your blog grows, you may need to scale:

**Heroku:**
```bash
heroku ps:scale web=2  # Scale to 2 dynos
heroku ps:type web=standard-1x  # Upgrade dyno type
```

**Railway/Render:**
- Upgrade your plan through the dashboard
- Increase instance size/replicas

## Support

For issues specific to this blog platform:
- Open an issue on GitHub
- Check existing documentation

For platform-specific issues:
- Consult the platform's documentation
- Contact platform support

---

**Congratulations!** Your blog is now deployed and ready to use. Happy blogging! 🎉
