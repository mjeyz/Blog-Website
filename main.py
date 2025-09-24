import os
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from datetime import date
import sqlite3
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user
from dotenv import load_dotenv
import smtplib
from flask_gravatar import Gravatar
import psycopg2

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = "34dfhdgfh46ydbjtytg"
Bootstrap5(app)
ckeditor = CKEditor(app)

# DATABASE PATH
DB_PATH = "postgres://postgres:9992@localhost:5432/postgres"
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="9992",
    host="localhost",
    port="5432"
)

# : Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


class User(UserMixin):
    def __init__(self, id, email, password, first_name, last_name):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name


@login_manager.user_loader
def load_user(user_id):
    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password, first_name, last_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(id=user[0], email=user[1], password=user[2], first_name=user[3], last_name=user[4])
    return None


def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                subtitle TEXT NOT NULL,
                date TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                img_url TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES user(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES blog_post (id) ON DELETE CASCADE
            )
            ''')
        conn.commit()


# init_db()

def init_postgres_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL
            )
        """)
        new_func(cur)
        conn.commit()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comment (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES blog_post (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()


def new_func(cur):
    conn.commit()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS blog_post (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                subtitle VARCHAR(500) NOT NULL,
                date VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                author VARCHAR(255) NOT NULL,
                img_url VARCHAR(500) NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)


init_postgres_db()


# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure user is logged in before checking ID
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)  # Forbidden access
        return f(*args, **kwargs)

    return decorated_function


# : Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        with psycopg2.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("You are already registered, please login instead", "danger")
                return redirect(url_for("login"))

            cursor.execute("INSERT INTO users (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)",
                           (email, hashed_password, first_name, last_name))
            conn.commit()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]
            user = User(id=user_id, email=email, password=hashed_password, first_name=first_name, last_name=last_name)

            login_user(user)
            flash("Registration successful! Welcome.", "success")
            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


# : Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with psycopg2.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password, first_name, last_name FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                flash("That email does not exist, please register first", category="danger")
                return redirect(url_for("register"))

            stored_password = user[2]
            if not check_password_hash(stored_password, password):
                flash("Incorrect password, please try again", category="danger")
                return redirect(url_for("login"))

            user_obj = User(id=user[0], email=user[1], password=user[2], first_name=user[3], last_name=user[4])
            login_user(user_obj)
            return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post")
        blog_post = cursor.fetchall()

    posts = [blog for blog in blog_post]
    return render_template("index.html", all_posts=posts, current_user=current_user, current_year=date.today().year)


# : Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def show_post(post_id):
    form = CommentForm()

    # Ensure only logged-in users can submit comments
    if form.validate_on_submit():
        if not current_user.is_authenticated:  # Check if the user is logged in
            flash("You must be logged in to comment.", "warning")
            return redirect(url_for("login"))  # Redirect to login page

        with psycopg2.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comment (text, author_id, post_id) VALUES (%s, %s, %s)",
                           (form.text.data, current_user.id, post_id))
            conn.commit()
        flash("Comment added successfully!", "success")
        return redirect(url_for("show_post", post_id=post_id))

    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Fetch the blog post details, using first_name and last_name instead of name
        post = cursor.execute('''
            SELECT blog_post.id, blog_post.title, blog_post.subtitle, blog_post.date, 
                   blog_post.body, blog_post.img_url, 
                   user.first_name || ' ' || user.last_name AS author
            FROM blog_post 
            JOIN user ON blog_post.author_id = user.id 
            WHERE blog_post.id = ?
        ''', (post_id,)).fetchone()

        if not post:
            return "Post not found", 404

        post_data = {
            "id": post[0],
            "title": post[1],
            "subtitle": post[2],
            "date": post[3],
            "body": post[4],
            "img_url": post[5],
            "author": post[6],
        }

        # Fetch comments with the first and last names of commenters
        comments = cursor.execute('''
            SELECT comment.text, user.email, user.id, user.first_name || ' ' || user.last_name AS commenter_name
            FROM comment
            JOIN user ON comment.author_id = user.id
            WHERE comment.post_id = ?
            ORDER BY comment.id DESC
        ''', (post_id,)).fetchall()

        comments_list = [{"text": c[0], "email": c[1], "id": c[2], "commenter_name": c[3]} for c in comments]

    return render_template("post.html", post=post_data, comments=comments_list, current_user=current_user, form=form)


# : Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        with psycopg2.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blog_post (title, subtitle, date, body, author, img_url, author_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                form.title.data,
                form.subtitle.data,
                date.today().strftime("%B %d, %Y"),
                form.body.data,
                form.author.data,
                form.img_url.data,
                current_user.id
            ))  # Add the author_id here

            conn.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


# : Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    form = CreatePostForm()

    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        post = cursor.execute("SELECT * FROM blog_post WHERE id = ?", (post_id,)).fetchone()
        if post is None:
            return "Post not found", 404

        if request.method == "POST" and form.validate_on_submit():
            cursor.execute(
                """
                UPDATE blog_post
                SET title = ?, body = ?, author = ?, img_url = ?, subtitle = ?
                WHERE id = ?
                """,
                (form.title.data, form.body.data, form.author.data, form.img_url.data, form.subtitle.data, post_id)
            )

            conn.commit()

            flash("Post updated successfully!", "success")
            return redirect(url_for("show_post", post_id=post_id))

        form.title.data = post[1]
        form.body.data = post[4]
        form.author.data = post[5]
        form.img_url.data = post[6]
        form.subtitle.data = post[2]

    return render_template("make-post.html", form=form, is_edit=True, current_user=current_user)


# : Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>", methods=["POST"])
@admin_only
def delete_post(post_id):
    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Fetch post to ensure it exists
        post = cursor.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,)).fetchone()

        if post is None:
            flash("Post not found.", "error")
            return redirect(url_for("get_all_posts"))

        # Delete the post
        cursor.execute("DELETE FROM blog_post WHERE id = ?", (post_id,))
        conn.commit()

        flash("Post deleted successfully!", "success")
        return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/download", methods=["GET", "POST"])
def download():
    return send_from_directory("static", path="files/MudasirAbbas.pdf", as_attachment=True)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        try:
            connection = smtplib.SMTP("smtp.gmail.com")
            connection.starttls()
            connection.login(user=os.getenv("EMAIL"), password=os.getenv("PASSWORD"))
            connection.sendmail(from_addr=email,
                                to_addrs=os.getenv("EMAIL"),
                                msg=f"subject:User Alert\n\n"
                                    f"Name: {name}\n"
                                    f"Email: {email}\n"
                                    f"Phone: {phone}\n"
                                    f"Message: {message}\n"
                                    f"Now it's time to contect him")
        except smtplib.SMTPException as e:
            print(f"Smtp Error: {e}")
        else:
            print("Successfully Sent your message")
            flash("Message Sent Successfully", "success")
        finally:
            connection.close()

    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
