import os
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import conn
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, EditProfileForm, ChangePasswordForm
from functions import save_picture, allowed_file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

# Initialize extensions
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Gravatar
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            user.first_name = user_data[2]
            user.last_name = user_data[3]
            user.email = user_data[4]
            user.password = user_data[5]
            user.joined_date = user_data[6]
            user.is_admin = user_data[7]
            
            # Get user profile info
            cur.execute("SELECT profile_image FROM user_info WHERE user_id = %s", (user_id,))
            profile_data = cur.fetchone()
            user.image_file = profile_data[0] if profile_data else 'default.jpg'
            
            return user
    return None


# User class for Flask-Login
class User(UserMixin):
    pass


# Admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Template context processor for helper functions
@app.context_processor
def utility_processor():
    def get_user_profile_image(user_id):
        with conn.cursor() as cur:
            cur.execute("SELECT profile_image FROM user_info WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            return result[0] if result else 'default.jpg'
    
    return dict(get_user_profile_image=get_user_profile_image)


# Routes
@app.route('/')
def get_all_posts():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM blog_post ORDER BY id DESC")
        result = cur.fetchall()
    return render_template("index.html", all_posts=result)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user email already exists
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
            user = cur.fetchone()
            
            if user:
                flash("You've already signed up with that email, log in instead!", "warning")
                return redirect(url_for('login'))
            
            # Create new user
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            
            cur.execute(
                "INSERT INTO users (username, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (form.email.data.split('@')[0], form.first_name.data, form.last_name.data, 
                 form.email.data, hash_and_salted_password)
            )
            new_user_id = cur.fetchone()[0]
            
            # Create user_info entry
            cur.execute(
                "INSERT INTO user_info (user_id, profile_image) VALUES (%s, %s)",
                (new_user_id, 'default.jpg')
            )
            conn.commit()
            
            # Log in the new user
            user = User()
            user.id = new_user_id
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.image_file = 'default.jpg'
            login_user(user)
            
            flash("Registration successful! Welcome to The Insight Hub!", "success")
            return redirect(url_for("get_all_posts"))
    
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cur.fetchone()
            
            if not user_data:
                flash("That email does not exist, please try again.", "danger")
                return redirect(url_for('login'))
            
            if not check_password_hash(user_data[5], password):
                flash('Password incorrect, please try again.', 'danger')
                return redirect(url_for('login'))
            
            # Create user object
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            user.first_name = user_data[2]
            user.last_name = user_data[3]
            user.email = user_data[4]
            user.password = user_data[5]
            user.joined_date = user_data[6]
            user.is_admin = user_data[7] if len(user_data) > 7 else False
            
            # Get profile image
            cur.execute("SELECT profile_image FROM user_info WHERE user_id = %s", (user.id,))
            profile_data = cur.fetchone()
            user.image_file = profile_data[0] if profile_data else 'default.jpg'
            
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('get_all_posts'))
    
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,))
        requested_post = cur.fetchone()
        
        if not requested_post:
            abort(404)
        
        # Get comments for this post
        cur.execute("""
            SELECT comment.id, comment.text, comment.author_id, 
                   users.first_name || ' ' || users.last_name as commenter_name,
                   users.email, comment.post_id, users.id as user_id
            FROM comment 
            JOIN users ON comment.author_id = users.id 
            WHERE comment.post_id = %s
            ORDER BY comment.id DESC
        """, (post_id,))
        comments = cur.fetchall()
        
        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("You need to login or register to comment.", "warning")
                return redirect(url_for("login"))
            
            cur.execute(
                "INSERT INTO comment (text, author_id, post_id) VALUES (%s, %s, %s)",
                (form.text.data, current_user.id, post_id)
            )
            conn.commit()
            flash('Your comment has been posted!', 'success')
            return redirect(url_for("show_post", post_id=post_id))
    
    # Convert tuple to dict-like object for template
    class Post:
        def __init__(self, data):
            self.id = data[0]
            self.title = data[1]
            self.subtitle = data[2]
            self.date = data[3]
            self.body = data[4]
            self.author = data[5]
            self.img_url = data[6]
            self.author_id = data[7]
    
    post = Post(requested_post)
    
    # Convert comments to list of dicts
    comment_list = []
    for comment in comments:
        comment_list.append({
            'id': comment[0],
            'text': comment[1],
            'author_id': comment[2],
            'commenter_name': comment[3],
            'email': comment[4],
            'post_id': comment[5],
            'user_id': comment[6]
        })
    
    return render_template("post.html", post=post, form=form, comments=comment_list)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO blog_post (title, subtitle, body, img_url, author, date, author_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (form.title.data, form.subtitle.data, form.body.data, form.img_url.data,
                 current_user.first_name + ' ' + current_user.last_name, date.today().strftime("%B %d, %Y"), current_user.id)
            )
            conn.commit()
        
        flash('Your post has been created!', 'success')
        return redirect(url_for("get_all_posts"))
    
    return render_template("make-post.html", form=form, is_edit=False)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM blog_post WHERE id = %s", (post_id,))
        post_data = cur.fetchone()
        
        if not post_data:
            abort(404)
        
        form = CreatePostForm(
            title=post_data[1],
            subtitle=post_data[2],
            img_url=post_data[6],
            author=post_data[5],
            body=post_data[4]
        )
        
        if form.validate_on_submit():
            cur.execute(
                "UPDATE blog_post SET title = %s, subtitle = %s, img_url = %s, author = %s, body = %s WHERE id = %s",
                (form.title.data, form.subtitle.data, form.img_url.data, form.author.data, form.body.data, post_id)
            )
            conn.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for("show_post", post_id=post_id))
    
    return render_template("make-post.html", form=form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM blog_post WHERE id = %s", (post_id,))
        conn.commit()
    
    flash('Post has been deleted!', 'success')
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    with conn.cursor() as cur:
        # Get user basic info
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        
        if not user_data:
            abort(404)
        
        # Get user extended info
        cur.execute("SELECT * FROM user_info WHERE user_id = %s", (user_id,))
        user_info = cur.fetchone()
        
        # Get user's posts
        cur.execute("SELECT * FROM blog_post WHERE author_id = %s ORDER BY id DESC", (user_id,))
        user_posts = cur.fetchall()
        
        # Check if current user is following this user
        is_following = False
        if current_user.is_authenticated:
            cur.execute(
                "SELECT * FROM followers WHERE follower_id = %s AND followed_id = %s",
                (current_user.id, user_id)
            )
            is_following = cur.fetchone() is not None
        
        # Get follower and following counts
        cur.execute("SELECT COUNT(*) FROM followers WHERE followed_id = %s", (user_id,))
        followers_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id = %s", (user_id,))
        following_count = cur.fetchone()[0]
    
    return render_template("profile.html", 
                         user=user_data, 
                         user_info=user_info, 
                         user_posts=user_posts,
                         is_user_following=is_following,
                         followers_count=followers_count,
                         following_count=following_count)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    with conn.cursor() as cur:
        # Get current user info
        cur.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
        user_data = cur.fetchone()
        
        cur.execute("SELECT * FROM user_info WHERE user_id = %s", (current_user.id,))
        user_info = cur.fetchone()
        
        form = EditProfileForm()
        
        if form.validate_on_submit():
            # Update users table
            cur.execute(
                "UPDATE users SET first_name = %s, last_name = %s, username = %s, email = %s WHERE id = %s",
                (form.first_name.data, form.last_name.data, form.username.data, 
                 form.email.data, current_user.id)
            )
            
            # Update user_info table
            visibility = True if form.visibility.data == 'public' else False
            
            if user_info:
                cur.execute("""
                    UPDATE user_info SET 
                        bio = %s, location = %s, occupation = %s, skill = %s, 
                        profession = %s, experience = %s, website = %s, education = %s,
                        linkedin = %s, github = %s, twitter = %s, facebook = %s, 
                        instagram = %s, profile_visibility = %s
                    WHERE user_id = %s
                """, (form.bio.data, form.location.data, form.occupation.data, form.skill.data,
                     form.profession.data, form.experience.data, form.website.data, form.education.data,
                     form.linkedin.data, form.github.data, form.twitter.data, form.facebook.data,
                     form.instagram.data, visibility, current_user.id))
            else:
                cur.execute("""
                    INSERT INTO user_info 
                    (user_id, bio, location, occupation, skill, profession, experience, 
                     website, education, linkedin, github, twitter, facebook, instagram, profile_visibility)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (current_user.id, form.bio.data, form.location.data, form.occupation.data, 
                     form.skill.data, form.profession.data, form.experience.data, form.website.data,
                     form.education.data, form.linkedin.data, form.github.data, form.twitter.data,
                     form.facebook.data, form.instagram.data, visibility))
            
            conn.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
        
        elif request.method == 'GET':
            # Pre-populate form
            form.first_name.data = user_data[2]
            form.last_name.data = user_data[3]
            form.username.data = user_data[1]
            form.email.data = user_data[4]
            
            if user_info:
                form.bio.data = user_info[13]
                form.location.data = user_info[5]
                form.occupation.data = user_info[4]
                form.skill.data = user_info[1]
                form.profession.data = user_info[6]
                form.experience.data = user_info[2]
                form.website.data = user_info[7]
                form.education.data = user_info[3]
                form.linkedin.data = user_info[8]
                form.github.data = user_info[9]
                form.twitter.data = user_info[10]
                form.facebook.data = user_info[11]
                form.instagram.data = user_info[12]
                form.visibility.data = 'public' if user_info[15] else 'private'
    
    return render_template("edit_profile.html", form=form)


@app.route("/upload-profile-pic", methods=["GET", "POST"])
@login_required
def upload_profile_pic():
    if request.method == 'POST':
        if 'profile_pic' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            picture_file = save_picture(file)
            
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE user_info SET profile_image = %s WHERE user_id = %s",
                    (picture_file, current_user.id)
                )
                conn.commit()
            
            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
        else:
            flash('Invalid file type! Please upload an image file (png, jpg, jpeg, gif)', 'danger')
    
    return render_template('upload_profile_pic.html')


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE id = %s", (current_user.id,))
            current_password_hash = cur.fetchone()[0]
            
            if not check_password_hash(current_password_hash, form.current_password.data):
                flash('Current password is incorrect!', 'danger')
                return redirect(url_for('change_password'))
            
            new_password_hash = generate_password_hash(
                form.new_password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            
            cur.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_password_hash, current_user.id)
            )
            conn.commit()
        
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))
    
    return render_template('change_password.html', form=form)


@app.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow(user_id):
    if user_id == current_user.id:
        flash("You cannot follow yourself!", "warning")
        return redirect(url_for('profile', user_id=user_id))
    
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s)",
                (current_user.id, user_id)
            )
            conn.commit()
            flash('You are now following this user!', 'success')
        except Exception as e:
            conn.rollback()
            flash('An error occurred. You may already be following this user.', 'danger')
    
    return redirect(url_for('profile', user_id=user_id))


@app.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow(user_id):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM followers WHERE follower_id = %s AND followed_id = %s",
            (current_user.id, user_id)
        )
        conn.commit()
    
    flash('You have unfollowed this user.', 'info')
    return redirect(url_for('profile', user_id=user_id))


@app.route("/download")
def download():
    # Placeholder for download functionality
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
