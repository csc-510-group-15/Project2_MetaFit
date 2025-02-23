# password_reset.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
import secrets
import smtplib
import ssl
from email.message import EmailMessage
import bcrypt

# Create a blueprint for password reset routes
password_reset_bp = Blueprint('password_reset', __name__, template_folder='templates')

def send_reset_email(email, reset_code):
    # Get mail settings from the app config
    sender = current_app.config.get('MAIL_USERNAME', 'yourapp@example.com')
    sender_password = current_app.config.get('MAIL_PASSWORD', 'your-email-password')
    subject = 'Your Password Reset Code'
    body = f'Your password reset code is: {reset_code}'
    
    try:
        em = EmailMessage()
        em['From'] = sender
        em['To'] = email
        em['Subject'] = subject
        em.set_content(body)
    
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, sender_password)
            smtp.sendmail(sender, email, em.as_string())
    except Exception as e:
        print(f"Error sending reset email: {e}")

@password_reset_bp.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        mongo = current_app.mongo  # assuming your PyMongo instance is assigned to app.mongo
        user = mongo.db.user.find_one({"email": email})
        if user:
            # Generate a random reset code (adjust length as needed)
            reset_code = secrets.token_urlsafe(6)
            mongo.db.password_resets.insert_one({
                "email": email,
                "reset_code": reset_code,
                "created_at": datetime.now()
            })
            send_reset_email(email, reset_code)
            flash('A reset code has been sent to your email.', 'info')
            # Redirect to the reset page and pass the email as a query parameter
            return redirect(url_for('password_reset.reset_password', email=email))
        else:
            flash('Email not found. Please check your email address.', 'danger')
    return render_template('forgot_password.html')

@password_reset_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    if not email:
        flash('No email provided for password reset.', 'danger')
        return redirect(url_for('password_reset.forgot_password'))
    if request.method == 'POST':
        reset_code = request.form.get('reset_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('password_reset.reset_password', email=email))
        mongo = current_app.mongo
        reset_entry = mongo.db.password_resets.find_one({"email": email, "reset_code": reset_code})
        if reset_entry:
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            mongo.db.user.update_one(
                {"email": email},
                {"$set": {"password": hashed_password}}
            )
            # Remove the reset entry so the code can’t be reused
            mongo.db.password_resets.delete_one({"email": email, "reset_code": reset_code})
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid reset code. Please try again.', 'danger')
    return render_template('reset_password.html', email=email)
