import os
import secrets

from PIL import Image


# Ensure the upload directory exists
def ensure_upload_dir():
    upload_dir = 'static/profile_pics'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir


# ------------Function to save and resize image----------------
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def save_picture(file):
    # Ensure upload directory exists
    upload_dir = ensure_upload_dir()

    # Generate random filename
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(file.filename)
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(upload_dir, picture_filename)

    # Resize and save image
    output_size = (125, 125)
    i = Image.open(file)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_filename
