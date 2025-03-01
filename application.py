"""
The primary application script. Logic routes through here
before loading webpages throughout the website.
"""
from datetime import datetime, timedelta
import os
import ssl
from email.message import EmailMessage
from time import time
from urllib.parse import quote
import random
import re
import smtplib
import secrets
import bcrypt
import requests
from pyotp import TOTP
# from apps import App
from flask import json
from flask import jsonify
# from utilities import Utilities
from flask import (
    render_template,
    session,
    url_for,
    flash,
    redirect,
    request,
    Flask,
)
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_apscheduler import APScheduler
from tabulate import tabulate
import openai
from forms import (
    HistoryForm,
    RegistrationForm,
    LoginForm,
    CalorieForm,
    UserProfileForm,
    EnrollForm,
    WorkoutForm,
    TwoFactorForm,
    getDate,
    QuestionForm,
)
from service import history as history_service


from model.meal_recommendation import recommend_meal_plan

# Import and register the password reset blueprint
from src.password_reset import password_reset_bp

app = Flask(__name__)

app.secret_key = 'secret'
if os.environ.get('DOCKERIZED'):
    # Use Docker-specific MongoDB URI
    app.config['MONGO_URI'] = 'mongodb://mongo:27017/test'
else:
    # Use localhost MongoDB URI
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
app.config['MONGO_CONNECT'] = False
mongo = PyMongo(app)
app.mongo = mongo
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfVuRUpAAAAAI3pyvwWdLcyqUvKOy6hJ_zFDTE_"
app.config[
    'RECAPTCHA_PRIVATE_KEY'] = "6LfVuRUpAAAAANC8xNC1zgCAf7V66_wBV0gaaLFv"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "bogusdummy123@gmail.com"
app.config['MAIL_PASSWORD'] = "helloworld123!"
mail = Mail(app)

scheduler = APScheduler()

badge_milestones = {"highest_streak": [0, 7, 14, 21],
                    "calories_eaten": [0, 20, 40, 80],
                    "calories_burned": [0, 2000, 4000, 6000]}
badge_milestones = {"highest_streak": [0, 7, 14, 21],
                    "calories_eaten": [0, 20, 40, 80],
                    "calories_burned": [0, 2000, 4000, 6000]}


def update_statistic(email, stat_name, value, is_increment=False):
    """
    Update the value associated with the given named statistic.
    Additionally, update the current user's
    badge levels to match the new value.
    """
    # email = session.get('email')
    if email is None:
        return

    try:
        value = float(value)
    except ValueError:
        # The provided value was not a valid Number; return early.
        return

    # If no entry exists for this user account, create it.
    if mongo.db.stats.find_one({'email': email}) is None:
        mongo.db.stats.insert_one({'email': email})
    if mongo.db.stats.find_one({'email': email}) is None:
        mongo.db.stats.insert_one({'email': email})

    # Record the new statistic value in a database.
    # If stat is 1, then $set 5 results in 5, while $inc results in 6.
    db_operation = "$inc" if is_increment else "$set"
    mongo.db.stats.update_one(
        {'email': email}, {db_operation: {stat_name: value}})
    updated_entry = mongo.db.stats.find_one({'email': email})

    # The following should really be a database, or a csv spreadsheet.
    if stat_name not in badge_milestones:
        return

    milestone_values = badge_milestones[stat_name]
    tiers = len(milestone_values)

    # Determine the highest level that the new value matches or exceeds.
    lvl = 1

    while lvl < tiers and milestone_values[lvl] <= updated_entry[stat_name]:
        lvl += 1
    lvl = min(len(milestone_values), lvl - 1)

    mongo.db.badges.update_one({'email': email}, {"$set": {stat_name: lvl}})
    mongo.db.badges.update_one({'email': email}, {"$set": {stat_name: lvl}})


@app.context_processor
def inject_cache_buster():
    """
    Busts the cache.
    """
    return {'cache_buster': time()}


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    """
    home() function displays the homepage of our website.
    route "/home" will redirect to home() function.
    input: The function takes session as the input
    Output: Out function will redirect to the login page
    """
    if session.get('email'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    """"
    login() function displays the Login form (login.html) template
    route "/login" will redirect to login() function.
    LoginForm() called and if the form is submitted
    then various values are fetched and verified
    from the database entries
    Input: Email, Password, Login Type
    Output: Account Authentication and redirecting to Dashboard
    """

    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            temp = mongo.db.user.find_one(
                {'email': form.email.data},
                {'email', 'username', 'password', 'last_login', 'streak'})
            if temp is not None and temp['email'] == form.email.data and (
                    bcrypt.checkpw(form.password.data.encode("utf-8"),
                                   temp['password'])
                    or temp['password'] == form.password.data):
                flash(
                    'You have been logged in!',
                    'success'
                )
                session['email'] = temp['email']
                session['username'] = temp['username']
                last_login = temp.get('last_login')
                if datetime.now().date() - last_login.date() == timedelta(
                        days=1):
                    mongo.db.user.update_one(
                        {'email': form.email.data},
                        {
                            "$inc": {"streak": 1},
                            "$set": {"last_login": datetime.now()},
                        }
                    )
                    update_statistic(session['email'],
                                     "highest_streak", 1, True)
                else:
                    mongo.db.user.update_one(
                        {'email': form.email.data},
                        {
                            "$set": {
                                "streak": 0,
                                "last_login": datetime.now(),
                            }
                        }
                    )
                    update_statistic(session['email'], "highest_streak", 0)
                temp1 = mongo.db.user.find_one({'email': form.email.data},
                                               {'streak'})
                print(f"temp1={temp1}\nsession={session}")
                session['streak'] = temp1['streak']
                return redirect(url_for('dashboard'))
            else:
                flash(
                    'Login Unsuccessful. Please check username and password',
                    'danger'
                )

    else:
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    register() function displays the
    Registration portal (register.html) template
    route "/register" will redirect to
    register() function.
    RegistrationForm() called and if the form is
    submitted then various values are
    fetched and updated into the database
    Input: Username, Email, Password,
    Confirm Password, current height,
    current weight, target weight, target date
    Output: Value update in the
    database and redirected to the dashboard
    """
    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')

            # Generate and save 2FA secret to the session
            secret_key = secrets.token_urlsafe(20).replace('=', '')
            totp = TOTP(secret_key)
            two_factor_secret = totp.secret
            session['two_factor_secret'] = two_factor_secret
            session['registration_data'] = {
                'username':
                request.form.get('username'),
                'email':
                email,
                'password':
                bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
                'weight':
                request.form.get('weight'),
                'height':
                request.form.get('height'),
                'target_weight':
                request.form.get('target_weight'),
                'start_date':
                datetime.now().strftime('%Y-%m-%d'),
                'target_date':
                request.form.get('target_date'),
                'completed_challenges':
                {}  # Initialize with an empty dictionary
            }
            send_2fa_email(email, two_factor_secret)
            # Redirect to 2FA verification page
            return redirect(url_for('verify_2fa'))
        else:
            return render_template('register.html',
                                   title='Register',
                                   form=form)
    else:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


app.register_blueprint(password_reset_bp)


def send_2fa_email(email, two_factor_secret):
    sender = 'burnoutapp123@gmail.com'
    password = 'xszyjpklynmwqsgh'
    receiver = email

    subject = 'Two-Factor Authentication Code'
    body = f'Your Two-Factor Authentication Code: {two_factor_secret}'

    try:

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receiver, em.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        flash(
            'Failed to send Two-Factor Authentication code. Please try again.',
            'danger'
        )


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    """
    Displays and updates the UserProfileForm.
    The user only needs to input:
      - Height (in cms)
      - Weight (in kgs)
      - Target Weight (in kgs)
    """
    if not session.get('email'):
        return redirect(url_for('login'))

    email = session.get('email')
    print("User email:", email)

    # Fetch existing profile data from the user collection
    existing_profile = mongo.db.user.find_one({'email': email}, {
        'height': 1,
        'weight': 1,
        'target_weight': 1
    })
    print("Existing profile:", existing_profile)

    # Initialize the form, binding POST data if present.
    form = UserProfileForm(request.form)

    # On GET requests, pre-fill the form with existing values (if any)
    if request.method == 'GET' and existing_profile:
        form.height.data = existing_profile.get('height')
        form.weight.data = existing_profile.get('weight')
        form.target_weight.data = existing_profile.get('target_weight')

    # Only process when the method is POST
    if request.method == 'POST':
        print("POST data:", request.form)
        if form.validate():
            # Get form values
            height = form.height.data
            weight = form.weight.data
            target_weight = form.target_weight.data

            try:
                if existing_profile:
                    result = mongo.db.user.update_one(
                        {'email': email},
                        {'$set': {
                            'height': height,
                            'weight': weight,
                            'target_weight': target_weight
                        }}
                    )
                    if result.modified_count > 0:
                        flash('User Profile Updated Successfully', 'success')
                    else:
                        flash('No changes were made', 'info')
                else:
                    result = mongo.db.user.insert_one({
                        'email': email,
                        'height': height,
                        'weight': weight,
                        'target_weight': target_weight
                    })
                    if result.inserted_id:
                        flash('User Profile Created Successfully', 'success')
                    else:
                        flash('Failed to create user profile', 'danger')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'danger')

            return redirect(url_for('user_profile'))
        else:
            print("Form validation errors:", form.errors)

    return render_template('user_profile.html',
                           status=True,
                           form=form,
                           existing_profile=existing_profile)


@app.route("/badges", methods=['GET', 'POST'])
def badges():
    email = session.get('email')
    if email is None:
        return redirect(url_for('login'))

    statsData = mongo.db.stats.find_one({'email': email})
    if statsData is None:
        mongo.db.stats.insert_one({'email': email})
        statsData = mongo.db.stats.find_one({'email': email})

    badgeData = mongo.db.badges.find_one({'email': email})
    if badgeData is None:
        mongo.db.badges.insert_one({'email': email})
        badgeData = mongo.db.badges.find_one({'email': email})

    for stat in ["calories_burned", "calories_eaten", "highest_streak"]:
        if stat not in statsData:
            update_statistic(session['email'], stat, 0)
        else:
            update_statistic(session['email'], stat,
                             int(float(statsData[stat])))

    # if badgeData is None:
    #     print("error!")
    #     render_template('badges.html', title='Badge Collection')

    return render_template('badges.html', title='Badge Collection',
                           milestoneData=badge_milestones, badgeData=badgeData)


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted
    then various values are fetched and updated
    into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    # now = datetime.now()
    # now = now.strftime('%Y-%m-%d')

    get_session = session.get('email')
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                food = request.form.get('food')
                selected_date = request.form.get('target_date')
                # cals = food.split(" ")
                match = re.search(r'\((\d+)\)', food)
                if match:
                    cals = int(match.group(1))
                else:
                    cals = 0
                # cals = int(cals[1][1:len(cals[1]) - 1])
                mongo.db.calories.insert_one({
                    'date': selected_date,
                    'email': email,
                    'calories': cals
                })
                update_statistic(
                    session['email'], "calories_eaten", int(float(cals)), True)
                flash('Successfully sent email and updated the data!',
                      'success')
                add_food_entry_email_notification(email, food, selected_date)
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', form=form)


def add_food_entry_email_notification(email, food, date):
    sender = 'burnoutapp123@gmail.com'
    password = 'xszyjpklynmwqsgh'
    receiver = email

    subject = 'New food entry recorded'
    body = f'You recorded a new entry for {food} on the date {date}'

    try:

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receiver, em.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        flash('Failed to send email but the entry is recorded', 'danger')


def add_burn_entry_email_notification(email, burn, date):
    sender = 'burnoutapp123@gmail.com'
    password = 'xszyjpklynmwqsgh'
    receiver = email

    subject = 'New burn entry recorded'
    body = f'You recorded a new entry of {burn} on  {date}'

    try:

        em = EmailMessage()
        em['From'] = sender
        em['To'] = receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receiver, em.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
        flash('Failed to send email but the entry is recorded', 'danger')


@app.route("/workout", methods=['GET', 'POST'])
def workout():
    # now = datetime.now()
    # now = now.strftime('%Y-%m-%d')
    get_session = session.get('email')
    if get_session is not None:
        form = WorkoutForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                burn = request.form.get('burnout')
                selected_date = request.form.get('target_date')

                mongo.db.calories.insert_one({
                    'date': selected_date,
                    'email': email,
                    'calories': -float(burn)
                })
                update_statistic(session['email'],
                                 "calories_burned", int(float(burn)), True)
                if float(burn) < 100:
                    existing_user_entry = mongo.db.bronze_list.find_one({
                        'date':
                        selected_date,
                        'users':
                        email
                    })
                    if existing_user_entry:
                        mongo.db.bronze_list.delete_one({
                            'date': selected_date,
                            'users': email
                        })
                if float(burn) > 100:
                    flash(
                        f'YaY!You are in bronze list: {selected_date}',
                        'success'
                    )
                    existing_user_entry = mongo.db.bronze_list.find_one({
                        'date':
                        selected_date,
                        'users':
                        email
                    })
                    if existing_user_entry:
                        mongo.db.bronze_list.update_one(
                            {'date': selected_date},
                            {'$addToSet': {
                                'users': email
                            }})
                    else:
                        mongo.db.bronze_list.insert_one({
                            'date': selected_date,
                            'users': [email]
                        })

                flash('Successfully sent email and updated the data!',
                      'success')
                add_burn_entry_email_notification(email, burn, selected_date)
                return redirect(url_for('workout'))
    else:
        return redirect(url_for('home'))
    return render_template('workout.html', form=form)


# New route to display the bronze list for the current day
@app.route("/bronze_list", methods=['GET', 'POST'])
def bronze_list_page():
    form = getDate()

    if request.method == 'POST' and form.validate_on_submit():
        today = form.target_date.data.strftime('%Y-%m-%d')

        bronze_list_cursor = mongo.db.bronze_list.find({'date': today})

        if bronze_list_cursor:
            bronze_users = []
            for bronze_doc in bronze_list_cursor:
                users = bronze_doc.get('users', [])
                # Add the users from the database
                bronze_users.extend(users)
                mongo.db.bronze_list.update_one({'_id': bronze_doc['_id']},
                                                {'$set': {
                                                    'users': users
                                                }})
        else:
            # If no document exists for today, create a new one
            mongo.db.bronze_list.insert_one({'date': today, 'users': users})
            bronze_users = users

        return render_template('bronze_list.html',
                               title='Bronze List',
                               form=form,
                               bronze_users=bronze_users)

    return render_template('bronze_list.html',
                           title='Bronze List',
                           form=form,
                           bronze_users=[])


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    # ############################
    # quiz() function displays the quiz start page.
    # The route "/quiz" triggers this function,
    # which initializes a form and renders the main layout template.
    # - Input: None (form is initialized but not directly used here).
    # - Output: Renders 'layout.html' as the quiz introduction or start page.
    # ############################
    # form = getDate()
    return render_template('layout.html')


@app.route("/water", methods=['GET', 'POST'])
def water():
    return render_template('water.html')


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    """
    question() function displays and processes each
    quiz question based on the provided question ID.
    The route "/question/<int:id>" triggers this function,
    which retrieves the question and handles user answers.
    - Input: Question ID (URL parameter),
    form submission with selected answer.
    - Output: If answer is correct, 10 points
    are added to the user's score;
    otherwise, no points are added.
              Redirects to the next question or
    the score page upon completion.
    """

    form = QuestionForm()
    q = mongo.db.questions.find_one({"q_id": id})

    if 'marks' not in session:
        session['marks'] = 0

    if not q:
        return redirect(url_for('score'))

    answer_mapping = {
        q['options']['a']: 'a',
        q['options']['b']: 'b',
        q['options']['c']: 'c',
        q['options']['d']: 'd'
    }

    if request.method == 'POST':
        option = request.form['options']
        option = answer_mapping.get(option)

        if option == q['ans']:
            session['marks'] += 10
        return redirect(url_for('question', id=id + 1))

    form.options.choices = [(q['options']['a'], q['options']['a']),
                            (q['options']['b'], q['options']['b']),
                            (q['options']['c'], q['options']['c']),
                            (q['options']['d'], q['options']['d'])]

    return render_template('question.html',
                           form=form,
                           q=q,
                           title='Question {}'.format(id),
                           score=session.get('marks'))


@app.route('/score', methods=['GET', 'POST'])
def score():
    """
    score() function displays the user's
    final score at the end of the quiz.
    The route "/score" triggers this function,
    rendering a final score summary page.
    - Input: None.
    - Output: Renders 'score.html' with the
    total score accumulated in the session.
    """

    return render_template('score.html',
                           title='Final Score',
                           score=session.get('marks', 0))


@app.route("/history", methods=['GET', 'POST'])
def history():
    """
    history() function displays the Historyform (history.html) template
    route "/history" will redirect to history() function.
    HistoryForm() called and if the form is submitted
    then various values are fetched and update into the database entries
    Input: Email, date
    Output: Value fetched and displayed
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = HistoryForm()

    # Find out the last 7 day's calories burnt by the user
    labels = []
    values = []
    pipeline = history_service.get_calories_per_day_pipeline(7)
    filtered_calories = mongo.db.calories.aggregate(pipeline)
    for calorie_each_day in filtered_calories:
        if calorie_each_day['_id'] == 'Other':
            continue
        net_calories = int(calorie_each_day['total_calories']) - 2000
        labels.append(calorie_each_day['date'])
        values.append(str(net_calories))

    # The first day when the user registered or started using the app
    user_start_date = mongo.db.user.find({'email': email})[0]['start_date']
    user_target_date = mongo.db.user.find({'email': email})[0]['target_date']
    target_weight = mongo.db.user.find({'email': email})[0]['target_weight']
    current_weight = mongo.db.user.find({'email': email})[0]['weight']

    # Find out the actual calories which user needed
    # to burn/gain to achieve goal from the start day
    target_calories_to_burn = history_service.total_calories_to_burn(
        target_weight=int(target_weight), current_weight=int(current_weight))

    # Find out how many calories user has gained or burnt uptill now
    calories_till_today = mongo.db.calories.aggregate(
        history_service.get_calories_burnt_till_now_pipeline(
            email, user_start_date))
    current_calories = 0
    for calorie in calories_till_today:
        current_calories += calorie['SUM']
    # current_calories = [x for x in calories_till_today][0]['SUM']
    # if len(list(calories_till_today)) != 0 else 0

    # Find out no of calories user has to burn/gain in future per day
    calories_to_burn = history_service.calories_to_burn(
        target_calories_to_burn,
        current_calories,
        target_date=datetime.strptime(user_target_date, '%Y-%m-%d'),
        start_date=datetime.strptime(user_start_date, '%Y-%m-%d'))

    return render_template('history.html',
                           form=form,
                           labels=labels,
                           values=values,
                           burn_rate=calories_to_burn,
                           target_date=user_target_date)


@app.route("/ajaxhistory", methods=['GET', 'POST'])
def ajaxhistory():
    """
    ajaxhistory() is a POST function that displays
    and fetches various information from the database.
    Route "/ajaxhistory" will redirect
    to ajaxhistory() function.
    Details corresponding to the given
    email address are fetched
    from the database entries.
    Input: Email, date
    Output: date, email, calories, burnout
    """
    email = get_session = session.get('email')
    if get_session is not None:
        if request.method == "POST":
            date = request.form.get('date')
            res = mongo.db.calories.find_one({
                'email': email,
                'date': date
            }, {'date', 'email', 'calories', 'burnout'})
            if res:
                return json.dumps({
                    'date': res['date'],
                    'email': res['email'],
                    'burnout': res['burnout'],
                    'calories': res['calories']
                }), 200, {
                    'ContentType': 'application/json'
                }
            else:
                return json.dumps({
                    'date': "",
                    'email': "",
                    'burnout': "",
                    'calories': ""
                }), 200, {
                    'ContentType': 'application/json'
                }


@app.route("/feed", methods=['GET', 'POST'])
def feed():
    """
    Open a webpage full of examples courses and classes for the
    user to peruse.
    """
    return render_template('feed.html')


@app.route("/friends", methods=['GET', 'POST'])
def friends():
    """
    Open a webpage where users can send and receive friend requests from
    other active users.
    """
    email = session.get('email')
    myFriends = list(
        mongo.db.friends.find({
            'sender': email,
            'accept': True
        }, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f['receiver'])

    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))

    pendingRequests = list(
        mongo.db.friends.find({
            'sender': email,
            'accept': False
        }, {'sender', 'receiver', 'accept'}))
    # Count the number of pending friend requests

    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(
        mongo.db.friends.find({
            'receiver': email,
            'accept': False
        }, {'sender', 'receiver', 'accept'}))
    pending_requests_count = len(pendingApprovals)
    if len(pendingApprovals):
        # Flash the count to be displayed in the template
        flash(f"You have {pending_requests_count} pending friend requests.",
              'info')
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])

    # Retrieve burn_rate and target_date from the user's data
    user_data = mongo.db.user.find_one({"email": email})
    burn_rate = user_data.get("burn_rate",
                              0)  # Adjust if burn_rate calculation differs
    target_date = user_data.get("target_date", "your goal date")

    # Create the shareable message
    # Ensure this is properly aligned with the preceding block
    if burn_rate > 0:
        shareable_message = (
            f"I’m working hard to gain {abs(burn_rate)} calories daily "
            f"to reach my goal by {target_date}! #CalorieApp"
        )
    else:
        shareable_message = (
            f"Burning {abs(burn_rate)} calories daily to stay on track for my "
            f"goal by {target_date}! #CalorieApp"
        )

    return render_template('friends.html',
                           allUsers=allUsers,
                           pendingRequests=pendingRequests,
                           active=email,
                           pendingReceivers=pendingReceivers,
                           pendingApproves=pendingApproves,
                           myFriends=myFriends,
                           myFriendsList=myFriendsList,
                           burn_rate=burn_rate,
                           target_date=target_date,
                           shareable_message=shareable_message)


@app.route("/send_email", methods=['GET', 'POST'])
def send_email():
    """
    send_email() function shares Calorie History with friend's email
    route "/send_email" will redirect to send_email()
    function which redirects to friends.html page.
    Input: Email
    Output: Calorie History Received on specified email
    """
    email = session.get('email')
    data = list(
        mongo.db.calories.find({'email': email},
                               {'date', 'email', 'calories', 'burnout'}))
    table = [['Date', 'Email ID', 'Calories', 'Burnout']]
    for a in data:
        tmp = [a['date'], a['email'], a['calories'], a['burnout']]
        table.append(tmp)

    friend_email = str(request.form.get('share')).strip()
    friend_email = str(friend_email).split(',')
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    # Storing sender's email address and password
    sender_email = "calorie.app.server@gmail.com"
    sender_password = "Temp@1234"

    # Logging in with sender details
    server.login(sender_email, sender_password)
    message = (
        'Subject: Calorie History\n\n'
        'Your Friend wants to share their calorie history with you!\n'
        '{}'.format(tabulate(table))
    )
    for e in friend_email:
        server.sendmail(sender_email, e, message)

    server.quit()

    myFriends = list(
        mongo.db.friends.find({
            'sender': email,
            'accept': True
        }, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f['receiver'])

    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))

    pendingRequests = list(
        mongo.db.friends.find({
            'sender': email,
            'accept': False
        }, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(
        mongo.db.friends.find({
            'receiver': email,
            'accept': False
        }, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])

    return render_template('friends.html',
                           allUsers=allUsers,
                           pendingRequests=pendingRequests,
                           active=email,
                           pendingReceivers=pendingReceivers,
                           pendingApproves=pendingApproves,
                           myFriends=myFriends,
                           myFriendsList=myFriendsList)


@app.route("/ajaxsendrequest", methods=['GET', 'POST'])
def ajaxsendrequest():
    """
    ajaxsendrequest() is a function that updates friend
    request information into database
    route "/ajaxsendrequest" will redirect to
    ajaxsendrequest() function.
    Details corresponding to given email address are fetched
    from the database entries and send request details updated
    Input: Email, receiver
    Output: DB entry of receiver info into database and
    return TRUE if success and FALSE otherwise
    """
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.insert_one({
            'sender': email,
            'receiver': receiver,
            'accept': False
        })
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'
            }
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'
    }


@app.route("/ajaxcancelrequest", methods=['GET', 'POST'])
def ajaxcancelrequest():
    """
    ajaxcancelrequest() is a function that updates
    friend request information into database
    route "/ajaxcancelrequest" will redirect
    to ajaxcancelrequest() function.
    Details corresponding to given email address are fetched
    from the database entries and cancel request details updated
    Input: Email, receiver
    Output: DB deletion of receiver info into database
    and return TRUE if success and FALSE otherwise
    """
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.delete_one({
            'sender': email,
            'receiver': receiver
        })
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'
            }
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'
    }


@app.route("/ajaxapproverequest", methods=['GET', 'POST'])
def ajaxapproverequest():
    """
    ajaxapproverequest() is a function that
    updates friend request information into database
    route "/ajaxapproverequest" will redirect
    to ajaxapproverequest() function.
    Details corresponding to given email address are fetched
    from the database entries and approve request details updated
    Input: Email, receiver
    Output: DB updation of accept as TRUE info into database
    and return TRUE if success and FALSE otherwise
    """
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.update_one(
            {
                'sender': receiver,
                'receiver': email
            },
            {"$set": {
                'sender': receiver,
                'receiver': email,
                'accept': True
            }})
        mongo.db.friends.insert_one({
            'sender': email,
            'receiver': receiver,
            'accept': True
        })
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'
            }
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'
    }


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    """
    dashboard() function displays the dashboard.html template
    route "/dashboard" will redirect to dashboard() function.
    dashboard() called and displays the list of activities
    Output: redirected to dashboard.html
    """
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', title='Dashboard')


@app.route("/yoga", methods=['GET', 'POST'])
def yoga():
    """
    yoga() function displays the yoga.html template
    route "/yoga" will redirect to yoga() function.
    A page showing details about yoga is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "yoga"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('yoga.html', title='Yoga', form=form)


@app.route("/swim", methods=['GET', 'POST'])
def swim():
    """
    swim() function displays the swim.html template
    route "/swim" will redirect to swim() function.
    A page showing details about swimming is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "swimming"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('swim.html', title='Swim', form=form)


@app.route("/abbs", methods=['GET', 'POST'])
def abbs():
    """
    abbs() function displays the abbs.html template
    route "/abbs" will redirect to abbs() function.
    A page showing details about abbs
    workout is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and
    redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "abbs"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('abbs.html', title='Abbs Smash!', form=form)


@app.route("/belly", methods=['GET', 'POST'])
def belly():
    """
    belly() function displays the belly.html template
    route "/belly" will redirect to belly() function.
    A page showing details about belly workout is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and
    redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "belly"
                mongo.db.user.insertOne({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('belly.html', title='Belly Burner', form=form)


@app.route("/core", methods=['GET', 'POST'])
def core():
    """
    core() function displays the belly.html template
    route "/core" will redirect to
    core() function.
    A page showing details about core workout is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "core"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
    else:
        return redirect(url_for('dashboard'))
    return render_template('core.html', title='Core Conditioning', form=form)


@app.route("/gym", methods=['GET', 'POST'])
def gym():
    """
    gym() function displays the gym.html template
    route "/gym" will redirect to gym() function.
    A page showing details about gym plan is shown and
    if clicked on enroll then DB updation done
    and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and
    redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "gym"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('gym.html', title='Gym', form=form)


@app.route("/walk", methods=['GET', 'POST'])
def walk():
    """
    walk() function displays the walk.html template
    route "/walk" will redirect to walk() function.
    A page showing details about walk plan is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment
    and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "walk"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('walk.html', title='Walk', form=form)


@app.route("/dance", methods=['GET', 'POST'])
def dance():
    """
    dance() function displays the dance.html template
    route "/dance" will redirect to dance() function.
    A page showing details about dance plan is shown and
    if clicked on enroll then DB updation done
    and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "dance"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('dance.html', title='Dance', form=form)


@app.route("/hrx", methods=['GET', 'POST'])
def hrx():
    """
    hrx() function displays the hrx.html template
    route "/hrx" will redirect to hrx() function.
    A page showing details about hrx plan is shown and
    if clicked on enroll then DB updation
    done and redirected to new_dashboard
    Input: Email
    Output: DB entry about enrollment and redirected to new dashboard
    """
    email = get_session = session.get('email')
    if get_session is not None:
        form = EnrollForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                enroll = "hrx"
                mongo.db.user.insert_one({'Email': email, 'Status': enroll})
            flash(f' You have succesfully enrolled in our {enroll} plan!',
                  'success')
            return render_template('new_dashboard.html', form=form)
            # return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    return render_template('hrx.html', title='HRX', form=form)


@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    """
    Verifies 2-factor authentication.
    """
    form = TwoFactorForm()  # Create a new form for 2FA verification

    if form.validate_on_submit():
        # Verify the entered 2FA code against the stored one in the session
        entered_code = form.two_factor_code.data
        stored_code = session.get('two_factor_secret')

        if stored_code and entered_code == stored_code:
            # 2FA code is correct, proceed with registration
            user_data = session.get('registration_data')
            session['email'] = user_data['email']
            user_data['last_login'] = datetime.now()
            user_data['streak'] = 1
            mongo.db.user.insert_one(user_data)
            session.pop('two_factor_secret')
            session.pop('registration_data')
            flash('Two-Factor Authentication successful! User registered.',
                  'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Two-Factor Authentication code. ', 'danger')
            flash('User registration failed. Please try again.', 'danger')
            if 'registration_data' in session:
                del session['registration_data']
            return redirect(url_for('register'))

    return render_template('verify_2fa.html', title='Verify 2FA', form=form)


def get_completion(prompt):
    """
    Obtains OpenAI's completion of the given prompt, then returns it.
    """
    query = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response = query.choices[0].text
    return response


@app.route("/chat", methods=['POST', 'GET'])
def query_view():
    """
    Opens the AI chatbot webpage.
    """
    if request.method == 'POST':
        prompt = request.form['prompt']
        response = get_completion(prompt)

        return jsonify({'response': response})
    return render_template('chat.html')


@app.route("/api/share", methods=['GET', 'POST'])
def log_share():
    """
    Logs each social share action to the backend.
    """
    user_id = session.get('email')  # Assuming the user ID is the email
    platform = request.json.get('platform')

    if not user_id or not platform:
        return jsonify({
            "status": "error",
            "message": "User or platform not specified"
        }), 400

    # Log share action (can be stored in DB if needed)
    print(f"User {user_id} shared on {platform}.")
    return jsonify({"status": "success"})


DAILY_CHALLENGES = [
    "Drink 8 glasses of water", "Walk 5,000 steps", "Avoid sugary drinks",
    "Eat at least 3 servings of vegetables", "Complete a 15-minute meditation",
    "Do a 30-minute workout", "Sleep for at least 7 hours"
]


@app.route('/daily_challenge', methods=['GET', 'POST'])
def daily_challenge():
    """
    Opens the Daily Challenges webpage.
    """
    user_email = session.get('email')
    if not user_email:
        # Redirect unauthorized users to the login page
        return redirect(url_for('login'))

    today = datetime.today().strftime('%Y-%m-%d')
    random.seed(today)
    daily_challenges = random.sample(DAILY_CHALLENGES, 3)

    user_data = mongo.db.users.find_one({"email": user_email},
                                        {"completed_challenges": 1}) or {}
    completed_challenges = user_data.get("completed_challenges", {})

    challenges_status = {}
    all_completed = True
    for challenge in daily_challenges:
        is_completed = completed_challenges.get(f"{today}_{challenge}", False)
        challenges_status[challenge] = is_completed
        if not is_completed:
            all_completed = False

    if request.method == 'POST':
        completed_challenge = request.form.get('completed_challenge')
        if completed_challenge and not challenges_status[completed_challenge]:
            mongo.db.users.update_one({"email": user_email}, {
                "$set": {
                    f"completed_challenges.{today}_{completed_challenge}": True
                }
            },
                upsert=True
            )
            flash(f"Challenge '{completed_challenge}' completed! Great job!",
                  "success")
            return redirect(url_for('daily_challenge'))

    # Define the shareable message if all challenges are completed
    shareable_message = ""
    if all_completed:
        shareable_message = (
            "I completed all my daily challenges today! "
            "Feeling great and staying on track with #CalorieApp."
        )
    return render_template('daily_challenge.html',
                           daily_challenges=daily_challenges,
                           challenges_status=challenges_status,
                           all_completed=all_completed,
                           shareable_message=shareable_message)


def get_weekly_summary(user_email):
    """
    Fetch weekly progress data for a user and
    prepare a summary with social sharing buttons.
    """
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)

    # Fetch calories burned in the last week
    calories_burned = mongo.db.calories.find({
        "email": user_email,
        "date": {
            "$gte": one_week_ago
        }
    })
    total_calories = sum(cal["calories"] for cal in calories_burned)

    # Fetch challenges completed in the last week
    user_data = mongo.db.users.find_one({"email": user_email},
                                        {"completed_challenges": 1}) or {}
    completed_challenges = user_data.get("completed_challenges", {})
    weekly_challenges = [
        challenge_date.split('_', 1)[1]
        for challenge_date, is_completed in completed_challenges.items()
        if is_completed and datetime.strptime(
            challenge_date.split('_', 1)[0], '%Y-%m-%d') >= one_week_ago
    ]

    # Customize the message body based on user data
    message_body = f"""
    <html>
    <body>
    <p>Hello!</p>

    <p>Here’s your weekly progress summary:</p>
    <ul>
        <li>Total calories burned this week: {total_calories}</li>
        <li>Challenges completed: {len(weekly_challenges)}</li>
    </ul>

    <p>Keep up the great work and stay
    motivated for the next week!</p>
    """
    # Social sharing message
    share_message = (
        f"I’ve burned {total_calories} calories and completed "
        f"{len(weekly_challenges)} challenges this week! #CalorieApp"
    )
    encoded_share_message = quote(share_message)
    # Social sharing buttons with inline CSS for styling
    twitter_url = (
        f"https://twitter.com/intent/tweet?text={encoded_share_message}"
    )
    facebook_url = (
        "https://www.facebook.com/sharer/sharer.php?"
        f"u=https://calorieapp.com&quote={encoded_share_message}"
    )
    # Include the share message and social sharing buttons in the email body
    message_body += f"""
    <p>{share_message}</p>
    <p>
        <a href="{twitter_url}"
           style="display:inline-block; padding:10px 20px; font-size:16px;
                  color:#fff; background-color:#1DA1F2; text-decoration:none;
                  border-radius:5px; margin-right:10px;">
            Share on Twitter
        </a>
        <a href="{facebook_url}"
           style="display:inline-block; padding:10px 20px; font-size:16px;
                  color:#fff; background-color:#3b5998; text-decoration:none;
                  border-radius:5px; margin-right:10px;">
            Share on Facebook
        </a>
    </p>
    <p>Best,<br>The CalorieApp Team</p>
    </body>
    </html>
    """

    return message_body


def send_weekly_email(user_email):
    """
    Sends the weekly progress summary email
    to the user with social sharing buttons.
    """
    # Generate the email body
    email_body = get_weekly_summary(user_email)
    subject = "Your Weekly Progress Summary"

    # Setup email message
    msg = EmailMessage()
    msg.set_content(email_body,
                    subtype='html')  # Use HTML format for clickable buttons
    msg["Subject"] = subject
    msg["From"] = app.config['MAIL_USERNAME']
    msg["To"] = user_email

    # Send the email using SMTP
    try:
        with smtplib.SMTP_SSL(app.config['MAIL_SERVER'],
                              app.config['MAIL_PORT']) as smtp:
            smtp.login(app.config['MAIL_USERNAME'],
                       app.config['MAIL_PASSWORD'])
            smtp.send_message(msg)
        print(f"Weekly summary sent to {user_email}")
    except Exception as e:
        print(f"Error sending weekly summary to {user_email}: {e}")


def scheduled_weekly_email():
    """
    Scheduled job to send weekly progress emails to all users.
    """
    try:
        # Retrieve all users from the database
        users = mongo.db.user.find({}, {"email": 1})
        for user in users:
            user_email = user["email"]
            send_weekly_email(user_email)
    except Exception as e:
        print(f"Error in scheduled weekly email job: {e}")


# Scheduler job configuration
scheduler.add_job(
    id="Weekly Email Job",
    func=scheduled_weekly_email,  # Note: No user_email argument needed
    trigger="cron",
    day_of_week="mon",
    hour=8,
    minute=0)


@app.route("/meal_plan", methods=['GET', 'POST'])
def meal_plan():
    """
    Renders the meal_plan.html template,
    where users can view their recommended meal plan.
    """
    return render_template("meal_plan.html", title="Meal Plan")


@app.route('/recommend_meal_plan', methods=['POST', 'GET'])
def recommend_meal_plan_endpoint():
    """
    Endpoint to recommend a meal plan based on user preferences.
    Receives JSON data with goal, calories, protein,
    carbs, and fat values, then generates a recommendation.
    """
    # Parse user data from the request
    user_data = request.json
    goal = user_data.get('goal')
    calories = user_data.get('calories')
    protein = user_data.get('protein')
    carbs = user_data.get('carbs')
    fat = user_data.get('fat')

    # Generate meal recommendations
    recommended_meals = recommend_meal_plan(goal, calories, protein, carbs,
                                            fat)
    return jsonify(recommended_meals)


# Example /bmi_advice endpoint update:


@app.route('/bmi_advice', methods=['GET', 'POST'])
def bmi_advice():
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    email = session.get('email')
    # Assuming user profile is in the user collection:
    profile = mongo.db.user.find_one({"email": email})
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    weight = profile.get("weight")
    height = profile.get("height")
    try:
        weight_val = float(weight)
        height_val = float(height)
        height_m = height_val / 100.0  # convert cm to meters
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid weight or height data"}), 400

    bmi = weight_val / (height_m ** 2)

    # (Your existing advice logic follows here...)
    if bmi < 18.5:
        advice = (
            "Your BMI suggests you are underweight."
            "Consider increasing your calorie and"
            "protein intake to help gain weight."
        )
        calorie_suggestion = "Consider setting a higher calorie goal."
        goal_suggestion = "Gain Weight"
    elif bmi < 25:
        advice = (
            "Your BMI is in the normal range."
            "Maintain your current balanced diet"
            "and exercise routine."
        )
        calorie_suggestion = "Your current calorie goal seems appropriate."
        goal_suggestion = "Maintenance"
    else:
        advice = (
            "Your BMI indicates you are overweight. "
            "A moderate calorie deficit with balanced"
            "macros might help you "
            "achieve your weight loss goals."
        )
        calorie_suggestion = "Consider lowering your calorie goal moderately."
        goal_suggestion = "Weight Loss"

    # Reference values based on the suggested goal (example for Weight Loss)
    reference_values = {}
    if goal_suggestion == "Weight Loss":
        reference_values = {
            "goal": "Weight Loss",
            "calories": 223,
            "protein": 3424,
            "carbs": 12,
            "fat": 15
        }
    elif goal_suggestion == "Maintenance":
        reference_values = {
            "goal": "Maintenance",
            "calories": 2000,
            "protein": 100,
            "carbs": 250,
            "fat": 70
        }
    elif goal_suggestion == "Gain Weight":
        reference_values = {
            "goal": "Gain Weight",
            "calories": 2500,
            "protein": 120,
            "carbs": 300,
            "fat": 80
        }

    return jsonify({
        "bmi": round(bmi, 2),
        "weight": weight,         # new field
        "height": height,         # new field
        "advice": advice,
        "calorie_suggestion": calorie_suggestion,
        "goal_suggestion": goal_suggestion,
        "reference_values": reference_values
    })


def process_guide_text(guide_text):
    # Remove any surrounding double quotes
    guide_text = guide_text.strip('"')
    # Find all segments that start with a digit+dot
    # (e.g. "1.") until next digit+dot or end.
    steps = re.findall(r'(\d+\..*?)(?=\s*\d+\.|$)', guide_text.strip())
    cleaned_steps = []
    for step in steps:
        # Remove the leading digits, dot,
        # and optional spaces: e.g. "1. " -> ""
        # so you get just "Cook Pasta – Boil pasta
        # according to package instructions..."
        cleaned = re.sub(r'^\d+\.\s*', '', step).strip()
        cleaned_steps.append(cleaned)
    return cleaned_steps


@app.route("/meal_guide", methods=['GET', 'POST'])
def meal_guide():
    food_name = request.args.get("food_name", "Unknown Meal")
    calories = request.args.get("calories", "N/A")
    protein = request.args.get("protein", "N/A")
    carbs = request.args.get("carbs", "N/A")
    fat = request.args.get("fat", "N/A")
    cook_guide = request.args.get("cook_guide", "No guide available")
    image_url = request.args.get(
        "image_url", "https://via.placeholder.com/300")
    image_url = request.args.get(
        "image_url", "https://via.placeholder.com/300")
    print(request.args)
    # Process the guide text into a list of steps.
    steps = process_guide_text(cook_guide)
    render = render_template("meal_guide.html",
                             food_name=food_name,
                             calories=calories,
                             protein=protein,
                             carbs=carbs,
                             fat=fat,
                             steps=steps,
                             image_url=image_url)

    return render


@app.after_request
def add_header(response):
    # Disable caching
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, public, max-age=0"
    )

    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/exercise", methods=["GET", "POST"])
def exercise():
    exercises = []
    error_message = None

    if request.method == "POST":
        muscle = request.form.get("muscle", "").strip()
        difficulty = request.form.get("difficulty", "").strip()

        if not muscle or not difficulty:
            error_message = "Both muscle and difficulty are required!"
            return render_template(
                "exercise.html",
                exercises=[], error_message=error_message
            )

        muscle = muscle.lower()
        difficulty = difficulty.lower()

        api_url = (
            f"https://api.api-ninjas.com/v1/exercises?"
            f"muscle={muscle}&difficulty={difficulty}"
        )
        headers = {'X-Api-Key': 'ThMgHV6VS4iYBAsvrUnNRg==vDzibI5DsOwhxevU'}
        resp = requests.get(api_url, headers=headers)

        if resp.status_code == 200:
            exercises = resp.json()[:5]  # Limit to 5 exercises
            if not exercises:
                error_message = (
                    "No exercises found for the specified muscle "
                    "and difficulty."
                )
        else:
            error_message = (
                f"Error {resp.status_code}: Unable to fetch exercises."
            )

    return render_template("exercise.html", exercises=exercises,
                           error_message=error_message)


if __name__ == "__main__":
    if os.environ.get('DOCKERIZED'):
        # Use Docker-specific MongoDB URI
        app.run(host='0.0.0.0', debug=True)
    else:
        app.run(debug=True)
