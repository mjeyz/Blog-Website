import psycopg2

# DATABASE PATH
DB_PATH = "postgres://postgres:9992@localhost:5432/postgres"
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="9992",
    host="localhost",
    port="5432"
)


def init_postgres_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(150),
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
        conn.commit()
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
        conn.commit()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS followers (
                id SERIAL PRIMARY KEY,
                follower_id INTEGER NOT NULL,
                followed_id INTEGER NOT NULL,
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                skill VARCHAR(100),
                Experience VARCHAR(100),
                Education VARCHAR(100),
                Occupation VARCHAR(100),
                location VARCHAR(100),
                profession VARCHAR(100),
                website VARCHAR(150),
                LinkedIn VARCHAR(100),
                GitHub VARCHAR(100),
                Twitter VARCHAR(100),
                Facebook VARCHAR(100),
                Instagram VARCHAR(100),
                bio VARCHAR(500),
                profile_image TEXT,
                profile_visibility BOOLEAN DEFAULT TRUE,
                user_id INTEGER UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


init_postgres_db()