import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail


class App:

    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'secret'
        if os.environ.get('DOCKERIZED'):
            self.app.config['MONGO_URI'] = 'mongodb://mongo:27017/test'
        else:
            self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
        self.mongo = PyMongo(self.app)
        self.app.config[
            'RECAPTCHA_PUBLIC_KEY'] = "6LfVuRUpAAAAAI3pyvwWdLcyqUvKOy6hJ_zFDTE_"
        self.app.config[
            'RECAPTCHA_PRIVATE_KEY'] = "6LfVuRUpAAAAANC8xNC1zgCAf7V66_wBV0gaaLFv"
        self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.app.config['MAIL_PORT'] = 465
        self.app.config['MAIL_USE_SSL'] = True
        self.app.config['MAIL_USERNAME'] = "bogusdummy123@gmail.com"
        self.app.config['MAIL_PASSWORD'] = "helloworld123!"
        self.mail = Mail(self.app)
