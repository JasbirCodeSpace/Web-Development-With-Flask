import os
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import ContactForm
from flask_mail import Mail, Message
from pathlib import Path
from dotenv import load_dotenv
from threading import Thread

env_path = Path('.')/'.env'
load_dotenv(dotenv_path = env_path)
app = Flask(__name__)
base_dir = Path(__file__).resolve().parent
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+str(base_dir/'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.environ.get('MAIL_PASSWORD')
app.config["MAIL_SUBJECT_PREFIX"] = '[FLASK APP Query]'
app.config['MAIL_SENDER'] = 'Admin <shikhawat.jasbir@gmail.com>'

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def send_mail_async(app, msg):
    with app.app_context():
        mail.send(msg)
def send_mail(name, email, subject, message, template):
    query = {'name':name, 'email':email, 'subject':subject, 'message':message}
    msg = Message(app.config.get('MAIL_SUBJECT_PREFIX')+subject, sender=app.config.get('MAIL_SENDER'), recipients = [email])
    msg.html = render_template(template+'.html',**query)
    mail_thread = Thread(target = send_mail_async, args=[app, msg]) 
    mail_thread.start()
    return mail_thread

@app.route('/', methods=['GET', 'POST'])
def contact():
    print(base_dir)
    form = ContactForm()
    if request.method == 'POST':
        flag = False
        if form.validate_on_submit():
            form_data = {'name': form.name.data, 'email': form.email.data, 'subject':form.subject.data, 'message':form.message.data}
            query = Query(**form_data)
            db.session.add(query)
            db.session.commit()
            send_mail(**form_data, template = 'mail/query')
            flag = True
            flash('Your message is successfully submitted')
            form.name.data = form.email.data = form.subject.data = form.message.data = ''
        else:
            flash('Invalid input')
        return render_template('contact.html', form = form, flag = flag)
    elif request.method == 'GET':
        return render_template('contact.html', form = form)


class Query(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    message = db.Column(db.Text, nullable = False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, email, subject, message):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
    
    def __str__(self):
        return f'<User {self.email}>'


