from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from src.models import User

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        username_exists = User.query.filter_by(username=username.data).first()
        if username_exists:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        email_exists = User.query.filter_by(email=email.data).first()
        if email_exists:
            raise ValidationError('Email already exists. Login or recover your password')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    image = FileField('Update Profile Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            username_exists = User.query.filter_by(username=username.data).first()
            if username_exists:
                raise ValidationError('Username already exists.')

    def validate_email(self, email):
        if email.data != current_user.email:
            email_exists = User.query.filter_by(email=email.data).first()
            if email_exists:
                raise ValidationError('Email already exists.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=20)])
    submit = SubmitField('Submit')

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=15)])
    send = SubmitField('Send')
