import os
from flask import Flask, render_template, redirect, url_for
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


@app.route('/')
def get_all_posts():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post")
        blog_post = cursor.fetchall()

    posts = [blog for blog in blog_post]
    return render_template("index.html", all_posts=posts)


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


# add_new_post() to create a new blog post
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


 # edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    form = CreatePostForm()

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

        return render_template("make-post.html", form=form, is_edit=True)


# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003) 