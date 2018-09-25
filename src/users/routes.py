import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from src import app, db, bcrypt
from src.models import User, Post
from src.users.forms import SignUpForm, LoginForm, UpdateAccountForm, PasswordRequestResetForm, PasswordResetForm
from src.users.utils import send_pw_reset_email, update_image
from src.main.utils import make_summary

users = Blueprint('users', __name__)

@users.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignUpForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account was successfully created. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/signup.html', title='Sign Up', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. Verify that you have entered your credentials correctly.', 'danger')

    return render_template('users/login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.image.data:
            image_file = update_image(form.image.data)
            if current_user.image != 'default.png':
                old_image_path = os.path.join(app.root_path, 'static/profile_imgs', current_user.image)
                os.remove(old_image_path)
            current_user.image = image_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account information has been updated.', 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for('static', filename=f'profile_imgs/{current_user.image}')
    return render_template('users/account.html', title='Your Account', image=image, form=form)

#Username in URL: remove spaces for - or disable spaces and add Display Name.
@users.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=3, page=page)
    make_summary(posts.items)
    return render_template('users/user.html', posts=posts, user=user, title=username)

@users.route("/request_pw_reset", methods=['GET', 'POST'])
def request_pw_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = PasswordRequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_pw_reset_email(user)
        flash(f'Instructions to reset your password have been emailed to {form.email.data}.', 'info')
        return redirect(url_for('users.login'))

    return render_template('users/request_reset.html', title='Password Recovery', form=form)


@users.route("/pw_reset/<token>", methods=['GET', 'POST'])
def pw_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('Expired or invalid token.', 'warning')
        return redirect(url_for('users.request_pw_reset'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/pw_reset.html', title='Reset Password', form=form)
