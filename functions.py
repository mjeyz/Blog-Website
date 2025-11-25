import os
import secrets
from PIL import Image
from database import conn


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


# ------------Function to save and resize image----------------
def save_picture(form_picture):
    from main import app  # Import inside the function

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)

    # Resize image
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
