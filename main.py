import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import sqlite3
from forms import CreatePostForm, RegisterForm, LoginForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "1234567890abcd"
Bootstrap5(app)
ckeditor = CKEditor(app)

# DATABASE PATH
DB_PATH = "instance/posts.db"

# : Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, password FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(id=user[0], email=user[1], name=user[2], password=user[3])
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
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                subtitle TEXT NOT NULL,
                date TEXT NOT NULL,
                body TEXT NOT NULL,
                img_url TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES user(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

init_db()


# : Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        name = form.name.data

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("You are already registered, please login instead", "danger")
                return redirect(url_for("login"))

            cursor.execute("INSERT INTO user (email, password, name) VALUES (?, ?, ?)",
                           (email, hashed_password, name))
            conn.commit()

            cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
            user_id = cursor.fetchone()[0]
            user = User(id=user_id, email=email, password=hashed_password, name=name)

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

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
            user = cursor.fetchone()

            if not user:
                flash("That email does not exist, please register first", category="danger")
                return redirect(url_for("register"))

            stored_password = user[2]
            if not check_password_hash(stored_password, password):
                flash("Incorrect password, please try again", category="danger")
                return redirect(url_for("login"))

            user_obj = User(id=user[0], email=user[1], password=user[2], name=user[3])
            login_user(user_obj)
            return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post")
        blog_post = cursor.fetchall()

    posts = [blog for blog in blog_post]
    return render_template("index.html", all_posts=posts, current_user=current_user)

# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>")
def show_post(post_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        post = cursor.execute('''
            SELECT blog_post.id, blog_post.title, blog_post.subtitle, blog_post.date, 
                   blog_post.body, blog_post.img_url, user.name 
            FROM blog_post 
            JOIN user ON blog_post.author_id = user.id 
            WHERE blog_post.id = ?
        ''', (post_id,)).fetchone()

    if post:
        post_data = {
            "id": post[0],
            "title": post[1],
            "subtitle": post[2],
            "date": post[3],
            "body": post[4],
            "img_url": post[5],
            "author": post[6],  # Correctly fetching the author's name
        }
    else:
        return "Post not found", 404

    return render_template("post.html", post=post_data, current_user=current_user)




# : Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blog_post (title, subtitle, date, body, author, img_url, author_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (form.title.data,
                  form.subtitle.data,
                  date.today().strftime("%B %d, %Y"),
                  form.body.data,
                  form.author.data,
                  form.img_url.data,
                  current_user.id))  # Add the author_id here

            conn.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


# : Use a decorator so only an admin user can edit a post

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = CreatePostForm()

    with sqlite3.connect(DB_PATH) as conn:
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
@login_required
def delete_post(post_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Fetch post to ensure it exists
        post = cursor.execute("SELECT * FROM blog_post WHERE id = ?", (post_id,)).fetchone()

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


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5003)