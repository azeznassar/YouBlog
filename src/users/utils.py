import os
import secrets
from flask import url_for
from flask_mail import Message
from PIL import Image
from src import app, mail

def update_image(selected_image):
    random_string = secrets.token_hex(6)
    _, file_ext = os.path.splitext(selected_image.filename)
    image_file_name = random_string + file_ext
    image_path = os.path.join(app.root_path, 'static/profile_imgs', image_file_name)

    output_size = (125, 125)
    image = Image.open(selected_image)
    image.thumbnail(output_size)

    image.save(image_path)
    return image_file_name

def send_pw_reset_email(user):
    token = user.get_reset_token()
    message = Message('YouBlog: Password Reset', sender=os.environ['SERVER_EMAIL'], recipients=[user.email])
    message.body = f'''To reset your password, visit the following link:
{url_for('users.pw_reset', token=token, _external=True)}

If you did not make this request then ignore this email, no changes will be made. 
'''
    mail.send(message)
