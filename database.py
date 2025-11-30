import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv("DB_NAME", "postgres"),
    'user': os.getenv("DB_USER", "postgres"),
    'password': os.getenv("DB_PASSWORD", "9992"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': os.getenv("DB_PORT", "5432")
}

# Create connection
conn = psycopg2.connect(**DB_CONFIG)


def init_postgres_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(150) UNIQUE,
                password VARCHAR(200),
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS blog_post (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL,
                date TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                img_url TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comment (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES blog_post (id) ON DELETE CASCADE
            )
        ''')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS followers (
                id SERIAL PRIMARY KEY,
                follower_id INTEGER NOT NULL,
                followed_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(follower_id, followed_id),
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id SERIAL PRIMARY KEY,
                skill VARCHAR(100),
                experience VARCHAR(100),
                education VARCHAR(100),
                occupation VARCHAR(100),
                location VARCHAR(100),
                profession VARCHAR(100),
                website VARCHAR(150),
                linkedin VARCHAR(100),
                github VARCHAR(100),
                twitter VARCHAR(100),
                facebook VARCHAR(100),
                instagram VARCHAR(100),
                bio TEXT,
                profile_image TEXT DEFAULT 'default.jpg',
                profile_visibility BOOLEAN DEFAULT TRUE,
                user_id INTEGER UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


init_postgres_db()
