import random

from flask_mail import Message
from apps import App
import string


class Utilities:
    app = App()
    mail = app.mail
    mongo = app.mongo

    def send_email(self, email):
        msg = Message()
        msg.subject = "BURNOUT - Reset Password Request"
        msg.sender = 'bogusdummy123@gmail.com'
        msg.recipients = [email]
        random = str(self.get_random_string(8))
        msg.body = 'Please use the \
            following password to login to your account: ' + random
        self.mongo.db.ath.update({'email': email}, {'$set': {'temp': random}})
        if self.mail.send(msg):
            return "success"
        else:
            return "failed"

    def get_random_string(self, length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        print("Random string of length", length, "is:", result_str)
        return result_str
