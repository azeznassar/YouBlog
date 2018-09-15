from flask import render_template, flash, redirect, url_for
from flask_login import login_user, current_user
from src import app, db, bcrypt
from src.forms import SignUpForm, LoginForm
from src.models import User, Post

posts = [
    {
        'author': 'Azez Nassar',
        'title': 'Blog Post 1',
        'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'date_posted': 'September 15, 2018'
    },
    {
        'author': 'John Doe',
        'title': 'Blog Post 2',
        'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'date_posted': 'September 17, 2018'
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts, title='Post and share your own blogs')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignUpForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Your account was successfully created. You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', title='Sign Up', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Verify that you have entered your credentials correctly.', 'danger')

    return render_template('login.html', title='Login', form=form)
