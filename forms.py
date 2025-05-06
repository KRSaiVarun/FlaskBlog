from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=20, message="Username must be 3–20 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Use at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.get_by_username(username.data)
        if user:
            raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user:
            raise ValidationError('That email is already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.get_by_username(username.data)
            if user:
                raise ValidationError('That username is already taken.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.get_by_email(email.data)
            if user:
                raise ValidationError('That email is already registered.')
