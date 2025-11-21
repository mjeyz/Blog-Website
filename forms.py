from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# : Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=4, max=25)])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Submit")


# : Create a LoginForm to log in existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Let Me In!")


# : Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, URLField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, URL, EqualTo
from flask_ckeditor import CKEditorField


class EditProfileForm(FlaskForm):
    # --- Basic Info ---
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=25)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    bio = CKEditorField("Bio", validators=[Optional(), Length(max=500)])
    location = StringField("Location", validators=[Optional(), Length(max=100)])

    # --- Professional / Personal Info ---
    occupation = StringField("Occupation", validators=[Optional(), Length(max=100)])
    skill = StringField("Skills", validators=[Optional(), Length(max=200)])  # e.g., "Python, Flask, SQL"
    profession = StringField("Professional Title", validators=[Optional(), Length(max=100)])
    experience = StringField("Experience", validators=[Optional(), Length(max=100)])
    website = URLField("Website / Portfolio", validators=[Optional(), URL(), Length(max=200)])
    education = StringField("Education / Institution", validators=[Optional(), Length(max=150)])

    # --- Social Links ---
    linkedin = URLField("LinkedIn Profile", validators=[Optional(), URL(), Length(max=200)])
    github = URLField("GitHub Profile", validators=[Optional(), URL(), Length(max=200)])
    twitter = URLField("Twitter Profile", validators=[Optional(), URL(), Length(max=200)])
    facebook = URLField("Facebook Profile", validators=[Optional(), URL(), Length(max=200)])
    instagram = URLField("Instagram Profile", validators=[Optional(), URL(), Length(max=200)])

    # --- Settings ---
    visibility = SelectField(
        "Profile Visibility",
        choices=[("public", "Public"), ("private", "Private")],
        validators=[DataRequired()],
        default="public"
    )
    allow_notifications = BooleanField("Enable Email Notifications")
    # --- Submit ---
    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[
        DataRequired(message="Please enter your current password.")
    ])

    new_password = PasswordField("New Password", validators=[
        DataRequired(message="Please enter a new password."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    confirm_password = PasswordField("Confirm New Password", validators=[
        DataRequired(message="Please confirm your new password."),
        EqualTo('new_password', message="Passwords must match.")
    ])

    submit = SubmitField("Change Password")
