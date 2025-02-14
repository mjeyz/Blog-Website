import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# TODO: Configure Flask-Login

# CREATE DATABASE
DB_PATH = "instance/posts.db"


def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(''''
            CREATE TABLE IF NOT EXISTS blog_post (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                subtitle TEXT NOT NULL,
                date TEXT NOT NULL,
                body TEXT NOT NULL,
                author TEXT NOT NULL,
                img_url TEXT NOT NULL,
                )
            ''')
        conn.commit()
        conn.close()


init_db()

# TODO: Create a User table for all your registered users.

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register')
def register():
    return render_template("register.html")


# TODO: Retrieve a user from the database based on their email.
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/logout')
def logout():
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post")
        blog_post = cursor.fetchall()

    posts = [blog for blog in blog_post]
    return render_template("index.html", all_posts=posts)

# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>")
def show_post(post_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        post = cursor.execute("SELECT * FROM blog_post WHERE id = ?", (post_id,)).fetchone()

    if post:
        post_data = {
            "id": post[0],
            "title": post[1],
            "subtitle": post[2],
            "date": post[3],
            "body": post[4],
            "author": post[5],
            "img_url": post[6],
        }
    else:
        return "Post not found", 404

    return render_template("post.html", post=post_data)


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blog_post (title, subtitle, date, body, author, img_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (form.title.data,
                  form.subtitle.data,
                  date.today().strftime("%B %d, %Y"),
                  form.body.data,
                  form.author.data,
                  form.img_url.data))
            conn.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)

# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
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
        form.body.data = post[3]
        form.author.data = post[4]
        form.img_url.data = post[5]
        form.subtitle.data = post[6]

    return render_template("make-post.html", form=form)

# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>", methods=["POST"])
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
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
