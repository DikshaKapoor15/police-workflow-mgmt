from flask import render_template
from app import app
from flask_mail import Mail
from flask_mail import Message
from app.models import *

# ...
mail=Mail(app)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


#asynchronous not done yet
def send_password_reset_email(user):
    print("in email.py --- reset password'''")
    token = user.get_reset_password_token()
    send_email(' Reset Your Password',
               sender="developmentsoftware305@gmail.com",
               recipients=[user.mail_id],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))