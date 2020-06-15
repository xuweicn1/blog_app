
from threading import Thread
from flask import render_template
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    """发送邮件"""

    token = user.get_reset_password_token()
    send_email('[博客站] 重置密码',
               sender=app.config['ADMINS'][0],
               text_body=render_template('email/reset_password.txt',user=user, token=token),
               recipients=[user.email],
               html_body=render_template('email/reset_password.html', user=user, token=token))
