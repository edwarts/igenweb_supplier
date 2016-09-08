from flask import current_app, render_template
from flask_mail import Mail, Message
import threading


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    t = threading.Thread(target=async_send, args=(app, msg))
    t.start()
    return


def async_send(app, msg):
    with app.app_context():
        mail = Mail()
        mail.init_app(app)
        mail.send(msg)
        return
