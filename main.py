import os
import smtplib
from datetime import date, timedelta
from functools import wraps

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from database import DB_CONFIG, init_postgres_db, conn
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, EditProfileForm, ChangePasswordForm
from functions import allowed_file, save_picture

load_dotenv()

# Initialize Flask app and configure extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("YOUR_SECRET_KEY") or "fallback-secret-key-12345"
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_PKG_TYPE'] = 'full'
app.config['CKEDITOR_CDN_URL'] = 'https://cdn.ckeditor.com/4.25.1-lts/full/ckeditor.js'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
Bootstrap5(app)
ckeditor = CKEditor(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='wavatar',
                    force_default=False,
                    force_lower=True,
                    use_ssl=True,
                    base_url=None)


class User(UserMixin):
    def __init__(self, id, email, password, first_name, last_name, username=None, joined_date=None, image_file="default.jpg", **kwargs):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.image_file = image_file
        self.username = username or ""
        self.joined_date = joined_date



@login_manager.user_loader
def load_user(user_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, password, first_name, last_name, username, joined_date
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

        if user:
            return User(
                id=user[0],
                email=user[1],
                password=user[2],
                first_name=user[3],
                last_name=user[4],
                username=user[5],
                joined_date=user[6]
            )
    return None


# Initialize the database
init_postgres_db()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# ------------ ROUTES -------------------- #
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("You are already registered, please login instead", "danger")
                return redirect(url_for("login"))

            cursor.execute(
                "INSERT INTO users (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)",
                (email, hashed_password, first_name, last_name)
            )
            conn.commit()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]
            user = User(id=user_id, email=email, password=hashed_password,
                        first_name=first_name, last_name=last_name)

            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
            flash("Registration successful! Welcome.", "success")
            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email, password, first_name, last_name FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()

            if not user:
                flash("That email does not exist, please register first", "danger")
                return redirect(url_for("register"))

            if not check_password_hash(user[2], password):
                flash("Incorrect password, please try again", "danger")
                return redirect(url_for("login"))

            user_obj = User(id=user[0], email=user[1], password=user[2],
                            first_name=user[3], last_name=user[4])
            login_user(user_obj, remember=form.remember.data, duration=timedelta(days=7))
            return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out successfully.", "warning")
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post ORDER BY id DESC")
        posts = cursor.fetchall()

    return render_template("index.html", all_posts=posts, current_user=current_user,
                           current_year=date.today().year)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def show_post(post_id):
    form = CommentForm()

    if form.validate_on_submit():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO comment (text, author_id, post_id) VALUES (%s, %s, %s)",
                (form.text.data, current_user.id, post_id)
            )
            conn.commit()
        flash("Comment added successfully!", "success")
        return redirect(url_for("show_post", post_id=post_id))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bp.id, bp.title, bp.subtitle, bp.date, bp.body, bp.img_url, 
                   bp.author_id, u.first_name || ' ' || u.last_name AS author
            FROM blog_post bp
            JOIN users u ON bp.author_id = u.id
            WHERE bp.id = %s
        ''', (post_id,))
        post = cursor.fetchone()

        if not post:
            flash("Post not found.", "danger")
            return redirect(url_for("get_all_posts"))

        post_data = {
            "id": post[0], "title": post[1], "subtitle": post[2], "date": post[3],
            "body": post[4], "img_url": post[5], "author_id": post[6], "author": post[7]
        }

        cursor.execute('''
            SELECT c.text, u.email, u.id, u.first_name || ' ' || u.last_name AS commenter_name
            FROM comment c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.id DESC
        ''', (post_id,))
        comments = [{"text": c[0], "email": c[1], "user_id": c[2], "commenter_name": c[3]}
                    for c in cursor.fetchall()]

    return render_template("post.html", post=post_data, comments=comments,
                           current_user=current_user, form=form)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO blog_post (title, subtitle, date, body, author, img_url, author_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                form.title.data, form.subtitle.data, date.today().strftime("%B %d, %Y"),
                form.body.data, form.author.data, form.img_url.data, current_user.id
            ))
            conn.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    form = CreatePostForm()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            return "Post not found", 404

        if form.validate_on_submit():
            cursor.execute('''
                UPDATE blog_post 
                SET title=%s, body=%s, author=%s, img_url=%s, subtitle=%s 
                WHERE id=%s
            ''', (form.title.data, form.body.data, form.author.data,
                  form.img_url.data, form.subtitle.data, post_id))
            conn.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for("show_post", post_id=post_id))

        form.title.data = post[1]
        form.body.data = post[4]
        form.author.data = post[5]
        form.img_url.data = post[6]
        form.subtitle.data = post[2]

    return render_template("make-post.html", form=form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>", methods=["POST"])
@admin_only
def delete_post(post_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blog_post WHERE id = %s", (post_id,))
        conn.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/download")
def download():
    return send_from_directory("static", path="files/MudasirAbbas.pdf", as_attachment=True)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        if not email:
            flash("Please provide your email address.", "danger")
            return render_template("contact.html", current_user=current_user)

        smtp_email = os.getenv("Your_SMTP_EMAIL")
        smtp_password = os.getenv("Your_SMTP_PASSWORD")

        if not smtp_email or not smtp_password:
            flash("Server email configuration is missing.", "danger")
        else:
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(smtp_email, smtp_password)
                    connection.sendmail(
                        from_addr=email,
                        to_addrs=smtp_email,
                        msg=f"Subject: User Alert\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
                    )
                flash("Message Sent Successfully", "success")
            except smtplib.SMTPException as e:
                flash(f"Failed to send email: {e}", "danger")

    return render_template("contact.html", current_user=current_user)


# -------------------- FOLLOW SYSTEM -------------------- #
@app.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (current_user.id, user_id)
        )
        conn.commit()
    flash("You are now following this user!", "success")
    return redirect(url_for("profile", user_id=user_id))


@app.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM followers WHERE follower_id=%s AND followed_id=%s",
            (current_user.id, user_id)
        )
        conn.commit()
    flash("You unfollowed this user.", "info")
    return redirect(url_for("profile", user_id=user_id))


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, first_name, last_name, email, username FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("get_all_posts"))

        cursor.execute('''
            SELECT skill, experience, education, occupation, location, website, 
                   linkedin, github, twitter, facebook, instagram, bio, profile_image
            FROM user_info WHERE user_id=%s
        ''', (user_id,))
        user_info = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM blog_post WHERE author_id=%s", (user_id,))
        posts_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM followers WHERE followed_id=%s", (user_id,))
        followers_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM followers WHERE follower_id=%s", (user_id,))
        following_count = cursor.fetchone()[0]

        cursor.execute("SELECT 1 FROM followers WHERE follower_id=%s AND followed_id=%s",
                       (current_user.id, user_id))
        is_user_following = cursor.fetchone() is not None

    return render_template("profile.html",
                           user=user, user_info=user_info, posts_count=posts_count,
                           followers_count=followers_count, following_count=following_count,
                           is_user_following=is_user_following, user_id=user_id
                           )


@app.route('/upload-profile-pic', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    if request.method == 'POST':
        if 'picture' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('profile', user_id=current_user.id))

        file = request.files['picture']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile', user_id=current_user.id))

        if file and allowed_file(file.filename):
            filename = save_picture(file)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_info (user_id, profile_image) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET profile_image = EXCLUDED.profile_image",
                    (current_user.id, filename)
                )
                conn.commit()
            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
        else:
            flash('Please upload a valid image file (PNG, JPG, JPEG, GIF).', 'danger')

    return render_template('upload_profile_pic.html', current_user=current_user)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        if request.method == "GET":
            cursor.execute("SELECT username, first_name, last_name, email FROM users WHERE id = %s", (current_user.id,))
            user = cursor.fetchone()
            if user:
                form.username.data = user[0]
                form.first_name.data = user[1]
                form.last_name.data = user[2]
                form.email.data = user[3]

            cursor.execute('''
                SELECT skill, experience, education, occupation, location, website, 
                       linkedin, github, twitter, facebook, instagram, bio, profession
                FROM user_info WHERE user_id = %s
            ''', (current_user.id,))
            info = cursor.fetchone()
            if info:
                form.skill.data = info[0]
                form.experience.data = info[1]
                form.education.data = info[2]
                form.occupation.data = info[3]
                form.location.data = info[4]
                form.website.data = info[5]
                form.linkedin.data = info[6]
                form.github.data = info[7]
                form.twitter.data = info[8]
                form.facebook.data = info[9]
                form.instagram.data = info[10]
                form.bio.data = info[11]
                form.profession.data = info[12]

        elif form.validate_on_submit():
            try:
                cursor.execute('''
                    UPDATE users SET username=%s, first_name=%s, last_name=%s, email=%s WHERE id=%s
                ''', (form.username.data, form.first_name.data, form.last_name.data, form.email.data, current_user.id))

                cursor.execute('''
                    INSERT INTO user_info (skill, experience, education, occupation, location, website,
                            linkedin, github, twitter, facebook, instagram, bio, profession, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        skill=EXCLUDED.skill, experience=EXCLUDED.experience, education=EXCLUDED.education,
                        occupation=EXCLUDED.occupation, location=EXCLUDED.location, website=EXCLUDED.website,
                        linkedin=EXCLUDED.linkedin, github=EXCLUDED.github, twitter=EXCLUDED.twitter,
                        facebook=EXCLUDED.facebook, instagram=EXCLUDED.instagram, bio=EXCLUDED.bio,
                        profession=EXCLUDED.profession
                ''', (
                    form.skill.data, form.experience.data, form.education.data, form.occupation.data,
                    form.location.data, form.website.data, form.linkedin.data, form.github.data,
                    form.twitter.data, form.facebook.data, form.instagram.data, form.bio.data,
                    form.profession.data, current_user.id
                ))
                conn.commit()
                flash("Profile updated successfully!", "success")
                return redirect(url_for("profile", user_id=current_user.id))
            except Exception as e:
                conn.rollback()
                flash(f"Error updating profile: {str(e)}", "error")

    return render_template("edit_profile.html", user=current_user, form=form)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            new_hashed_password = generate_password_hash(form.new_password.data)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_hashed_password, current_user.id))
                conn.commit()
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
    return render_template('change_password.html', form=form)


if __name__ == "__main__":
    app.run(debug=True, port=5003)