import os
import secrets
import smtplib
import psycopg2
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from datetime import date, timedelta

from werkzeug.utils import secure_filename

from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, EditProfileForm, ChangePasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user
from dotenv import load_dotenv
from flask_gravatar import Gravatar
from PIL import Image


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = "34dfhdgfh46ydbjtytg"
Bootstrap5(app)
ckeditor = CKEditor(app)

app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_PKG_TYPE'] = 'full'
app.config['CKEDITOR_CDN_URL'] = 'https://cdn.ckeditor.com/4.25.1-lts/full/ckeditor.js'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

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
                    default='wavatar',
                    force_default=False,
                    force_lower=True,
                    use_ssl=True,
                    base_url=None)


# Function to save and resize image
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)

    # Resize like Google
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


class User(UserMixin):
    def __init__(
        self,
        id,
        email,
        password,
        first_name,
        last_name,
        username=None,
        profession=None,
        location=None,
        website=None,
        bio=None,
        joined_date=None,
        image_file="default.jpg"
    ):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.image_file = image_file
        self.username = username or ""
        self.profession = profession or ""
        self.location = location or ""
        self.website = website or ""
        self.bio = bio or ""
        self.joined_date = joined_date

@login_manager.user_loader
def load_user(user_id):
    with psycopg2.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, password, first_name, last_name,
                   username, profession, location, website, bio
            FROM users
            WHERE id = %s
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
                profession=user[6],
                location=user[7],
                website=user[8],
                bio=user[9]
            )
    return None




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
                location VARCHAR(100),
                profession VARCHAR(100),
                website VARCHAR(150),
                bio TEXT
            )
        """)
        new_func(cur)
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

def new_func(cur):
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

            login_user(user, remember=form.remember.data, duration=timedelta(days=7))
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
            login_user(user_obj, remember=form.remember.data, duration=timedelta(days=7))
            return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out successfully.", category="warning")
    return redirect(url_for('get_all_posts'))


@app.route('/', methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
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

    try:
        with psycopg2.connect(DB_PATH) as conn:
            cursor = conn.cursor()
                
            # Fetch the blog post details, including author_id
            cursor.execute('''
                SELECT blog_post.id, blog_post.title, blog_post.subtitle, blog_post.date,
                       blog_post.body, blog_post.img_url, blog_post.author_id,
                       users.first_name || ' ' || users.last_name AS author
                FROM blog_post
                JOIN users ON blog_post.author_id = users.id
                WHERE blog_post.id = %s
            ''', (post_id,))
            post = cursor.fetchone()

            if post is None:
                flash("Post not found.", "danger")
                return redirect(url_for("get_all_posts"))

            post_data = {
                "id": post[0],
                "title": post[1],
                "subtitle": post[2],
                "date": post[3],
                "body": post[4],
                "img_url": post[5],
                "author_id": post[6],
                "author": post[7],  
            }

            cursor.execute('''
                SELECT comment.text, users.email, users.id, users.first_name || ' ' || users.last_name AS commenter_name
                FROM comment
                JOIN users ON comment.author_id = users.id
                WHERE comment.post_id = %s
                ORDER BY comment.id DESC
            ''', (post_id,))
            comments = cursor.fetchall()
            comments_list = [{"text": c[0], "email": c[1], "user_id": c[2], "commenter_name": c[3]} for c in comments]
    except Exception as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for("get_all_posts"))

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
        cursor.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        if post is None:
            return "Post not found", 404

        if request.method == "POST" and form.validate_on_submit():
            cursor.execute(
                """
                UPDATE blog_post
                SET title = %s, body = %s, author = %s, img_url = %s, subtitle = %s
                WHERE id = %s
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
        cursor.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,))
        post = cursor.fetchone()

        if post is None:
            flash("Post not found.", "error")
            return redirect(url_for("get_all_posts"))

        # Delete the post
        cursor.execute("DELETE FROM blog_post WHERE id = %s", (post_id,))
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

        if not email:
            flash("Please provide your email address.", "danger")
        else:
            smtp_email = "thisismjeyz@gmail.com"
            smtp_password = "gicx goix fiau uxjl"
            if not smtp_email or not smtp_password:
                flash("Server email configuration is missing.", "danger")
            else:
                connection = None
                try:
                    connection = smtplib.SMTP("smtp.gmail.com", 587)
                    connection.starttls()
                    connection.login(user=smtp_email, password=smtp_password)
                    connection.sendmail(from_addr=email,
                                            to_addrs=smtp_email,
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
                    if connection:
                        connection.close()


    return render_template("contact.html", current_user=current_user)

# -------------------- FOLLOW SYSTEM -------------------- #
@app.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow(user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM followers WHERE follower_id=%s AND followed_id=%s", (current_user.id, user_id))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s)", (current_user.id, user_id))
        conn.commit()
    cur.close()
    flash("You are now following this user!", "success")
    return redirect(url_for("profile", user_id=user_id))


@app.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow(user_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM followers WHERE follower_id=%s AND followed_id=%s", (current_user.id, user_id))
    conn.commit()
    cur.close()
    flash("You unfollowed this user.", "info")
    return redirect(url_for("profile", user_id=user_id))


def is_following(current_user_id, target_user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM followers WHERE follower_id=%s AND followed_id=%s", (current_user_id, target_user_id))
    result = cur.fetchone()
    cur.close()
    return result is not None


def count_followers(user_id):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE followed_id=%s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def count_following(user_id):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id=%s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    cur = conn.cursor()

    # Fetch target user info
    cur.execute("""
        SELECT id, first_name, last_name, email, bio, location, profession, website
        FROM users WHERE id=%s
    """, (user_id,))
    user = cur.fetchone()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("home"))

    # Count posts, followers, and following
    cur.execute("SELECT COUNT(*) FROM blog_post WHERE author_id=%s", (user_id,))
    posts_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM followers WHERE followed_id=%s", (user_id,))
    followers_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id=%s", (user_id,))
    following_count = cur.fetchone()[0]

    # Check if the current user already follows this user
    cur.execute("SELECT 1 FROM followers WHERE follower_id=%s AND followed_id=%s",
                (current_user.id, user_id))
    is_user_following = cur.fetchone() is not None

    cur.close()
    return render_template("profile.html",
                           user=user,
                           posts_count=posts_count,
                           followers_count=followers_count,
                           following_count=following_count,
                           is_user_following=is_user_following,
                           user_id=user_id)



# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload-profile-pic', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'picture' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.referrer or url_for('profile', user_id=current_user.id))

        file = request.files['picture']

        # Check if the file has a filename
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.referrer or url_for('profile', user_id=current_user.id))

        # Validate the file
        if file and allowed_file(file.filename):
            # Secure the filename and create a unique name
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save the file
            file.save(file_path)

            # Update the current_user object
            current_user.image_file = unique_filename
            # Save to JSON or file storage if needed

            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
        else:
            flash('Please upload a valid image file (PNG, JPG, JPEG, GIF).', 'danger')
            return redirect(request.referrer or url_for('profile', user_id=current_user.id))

    # GET request: render the upload template
    return render_template('upload_profile_pic.html')  # your template file name


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()

    cur = conn.cursor()

    if request.method == "GET":
        cur.execute("""
            SELECT username, first_name, last_name, email, location, profession, website, bio
            FROM users WHERE id = %s
        """, (current_user.id,))
        user = cur.fetchone()

        if user:
            form.username.data = user[0]
            form.first_name.data = user[1]
            form.last_name.data = user[2]
            form.email.data = user[3]
            form.location.data = user[4]
            form.profession.data = user[5]
            form.website.data = user[6]
            form.bio.data = user[7]

    elif form.validate_on_submit():
        cur.execute("""
            UPDATE users
            SET username = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                location = %s,
                profession = %s,
                website = %s,
                bio = %s
            WHERE id = %s
        """, (
            form.username.data,
            form.first_name.data,
            form.last_name.data,
            form.email.data,
            form.location.data,
            form.profession.data,
            form.website.data,
            form.bio.data,
            current_user.id
        ))

        conn.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile", user_id=current_user.id))


    return render_template("edit_profile.html", user=current_user, form=form)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('profile'))
    return render_template('change_password.html', form=form)



if __name__ == "__main__":
    app.run(debug=True, port=5003)
