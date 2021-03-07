import os
from flask import Flask, render_template, request, flash
from forms import ContactForm
from flask_mail import Mail, Message
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.')/'.env'
load_dotenv(dotenv_path = env_path)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config["MAIL_SERVER"] = os.environ['MAIL_SERVER']
app.config["MAIL_PORT"] = os.environ['MAIL_PORT']
app.config["MAIL_USE_SSL"] = os.environ['MAIL_USE_SSL']
app.config["MAIL_USERNAME"] = os.environ['MAIL_USERNAME']
app.config["MAIL_PASSWORD"] = os.environ['MAIL_PASSWORD']
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        flag = False
        if form.validate_on_submit():
            msg = Message(form.subject.data, sender=form.email.data, recipients = [app.config['MAIL_USERNAME']])
            msg.body = f"Name: {form.name.data}\r\nEmail: {form.email.data}\r\nSubject: {form.subject.data}\r\nQuery: {form.message.data}"
            mail.send(msg)
            flag = True
            flash('Your message is successfully submitted')
            form.name.data = form.email.data = form.subject.data = form.message.data = ''
        else:
            flash('Invalid input')
        return render_template('contact.html', form = form, flag = flag)
    elif request.method == 'GET':
        return render_template('contact.html', form = form)

@app.route('/user/<name>')
def user(name):
    return f'Hello {name}'