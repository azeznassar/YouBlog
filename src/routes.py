import os
import secrets
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from PIL import Image
import flask_whooshalchemy
from src import app, db, bcrypt, mail
from src.forms import (SignUpForm, LoginForm, UpdateAccountForm, PostForm,
                       ContactForm, PasswordRequestResetForm, PasswordResetForm, SearchForm)
from src.models import User, Post

def make_summary(posts):
    for p in posts:
        p.content = p.content[:60] + '...'
        p.content = " ".join(p.content.splitlines())

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    make_summary(posts.items)
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
        flash('Your account was successfully created. You are now able to log in.', 'success')
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
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed. Verify that you have entered your credentials correctly.', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def update_image(selected_image):
    random_string = secrets.token_hex(6)
    _, file_ext = os.path.splitext(selected_image.filename)
    image_file_name = random_string + file_ext
    image_path = os.path.join(app.root_path, 'static/profile_imgs', image_file_name)

    output_size = (125, 125)
    image = Image.open(selected_image)
    image.thumbnail(output_size)

    image.save(image_path)
    return image_file_name

@app.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for('static', filename=f'profile_imgs/{current_user.image}')
    return render_template('account.html', title='Your Account', image=image, form=form)

@app.route("/submit", methods=['GET', 'POST'])
@login_required
def submit_post():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your blog post has been submitted', 'success')
        return redirect(url_for('home'))

    return render_template('submit.html', title='Submit a post', legend='Submit a blog post', form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    current_post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=current_post.title, post=current_post)

@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    current_post = Post.query.get_or_404(post_id)

    if current_post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        current_post.title = form.title.data
        current_post.content = form.content.data
        db.session.commit()
        flash('Your post have been updated.', 'success')
        return redirect(url_for('post', post_id=current_post.id))

    elif request.method == 'GET':
        form.title.data = current_post.title
        form.content.data = current_post.content

    return render_template('submit.html', title='Edit post', legend='Edit your blog post', form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    current_post = Post.query.get_or_404(post_id)

    if current_post.author != current_user:
        abort(403)

    db.session.delete(current_post)
    db.session.commit()
    flash('Your post have been deleted.', 'success')
    return redirect(url_for('home'))

#Username in URL: remove spaces for - or disable spaces and add Display Name.
@app.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=3, page=page)
    for p in posts.items:
        p.content = p.content[:60] + '...'
        p.content = " ".join(p.content.splitlines())

    return render_template('user.html', posts=posts, user=user, title=username)

@app.route("/archive")
def sort_by_oldest():
    posts = Post.query.all()
    for p in posts:
        p.content = p.content[:60] + '...'
        p.content = " ".join(p.content.splitlines())

    return render_template('posts.html', posts=posts, title='Oldest blog posts')

def send_contact_email(name, email, msg):
    message = Message(f'Message from {name}', sender=email, recipients=[os.environ['SERVER_EMAIL']])
    message.body = msg + f'\nReply email address: {email}'
    mail.send(message)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        send_contact_email(form.name.data, form.email.data, form.message.data)
        flash('Your message has been sent.', 'success')
        return redirect(url_for('contact'))

    elif request.method == 'GET':
        if current_user.is_authenticated:
            form.email.data = current_user.email

    return render_template('contact.html', title='Contact', form=form)

def send_pw_reset_email(user):
    token = user.get_reset_token()
    message = Message('YouBlog: Password Reset', sender=os.environ['SERVER_EMAIL'], recipients=[user.email])
    message.body = f'''To reset your password, visit the following link:
{url_for('pw_reset', token=token, _external=True)}

If you did not make this request then ignore this email, no changes will be made. 
'''
    mail.send(message)

@app.route("/request_pw_reset", methods=['GET', 'POST'])
def request_pw_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = PasswordRequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_pw_reset_email(user)
        flash(f'Instructions to reset your password have been emailed to {form.email.data}.', 'info')
        return redirect(url_for('login'))

    return render_template('request_reset.html', title='Password Recovery', form=form)


@app.route("/pw_reset/<token>", methods=['GET', 'POST'])
def pw_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('Expired or invalid token.', 'warning')
        return redirect(url_for('request_pw_reset'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('pw_reset.html', title='Reset Password', form=form)


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('search_results', query=form.search.data))

    return render_template('search.html', title='Search', form=form)

@app.route('/search_results/<query>')
def search_results(query):
    results = Post.query.whoosh_search(query)
    make_summary(results)
    return render_template('search_results.html', query=query, results=results)
