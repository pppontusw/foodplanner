from threading import Thread
from flask_mail import Message
from flask import render_template, current_app
from app import mail

def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
  if current_app.config['MAIL_SERVER']:
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(
        current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
  token = user.get_reset_password_token()
  send_email('[{}] Reset Your Password'.format(current_app.config['APPLICATION_NAME']),
             sender=current_app.config['MAIL_DEFAULT_SENDER'],
             recipients=[user.email],
             text_body=render_template('auth/email/reset_password.txt',
                                       user=user, token=token),
             html_body=render_template('auth/email/reset_password.html',
                                       user=user, token=token))

def send_user_confirmation_email(user, confirm_url):
  send_email('[{}] Confirm Your Email'.format(current_app.config['APPLICATION_NAME']),
             sender=current_app.config['MAIL_DEFAULT_SENDER'],
             recipients=[user.email],
             text_body=render_template('auth/email/activate.txt',
                                       user=user, confirm_url=confirm_url),
             html_body=render_template('auth/email/activate.html',
                                       user=user, confirm_url=confirm_url))
