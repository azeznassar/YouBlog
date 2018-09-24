import os
from flask_mail import Message
from src import mail

def send_contact_email(name, email, msg):
    message = Message(f'Message from {name}', sender=email, recipients=[os.environ['SERVER_EMAIL']])
    message.body = msg + f'\nReply email address: {email}'
    mail.send(message)
    