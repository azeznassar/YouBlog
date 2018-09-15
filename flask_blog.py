import os
from flask import Flask, render_template, flash, redirect, url_for
from forms import SignUpForm, LoginForm
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

posts = [ # list not array 
    { # dictionary not object
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
    form = SignUpForm()
    if form.validate_on_submit():
        flash(f'Account successfully created for {form.username.data}', 'success')
        return redirect(url_for('home'))
    
    return render_template('signup.html', title='Sign Up', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'testing':
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Verify that you have entered your credentials correctly.', 'danger')

    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True)