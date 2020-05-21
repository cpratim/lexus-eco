from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Email, EqualTo, Length
from wtforms import StringField, PasswordField, FileField

class RegisterForm(FlaskForm):
    email = StringField('Email Address', validators=[Email(message='Invalid Email'), InputRequired('Please Input Something')])
    password = PasswordField('Password', validators=[InputRequired('Please Input Something'), Length(min=6, message='Password Must Be longer than 6 characters')])
    confirm = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords do not match')])
    normal_bus = StringField('Normal Bus Number', validators=[InputRequired('Please Input Something')])

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[Email(message='Invalid Email'), InputRequired('Please Input Something')])
    password = PasswordField('Password', validators=[InputRequired('Please Input Something')])

class VerifyForm(FlaskForm):
    code = StringField('Auth Code', validators=[InputRequired('Please Input Something')])

class DriverForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Please Input Something')])
    password = PasswordField('Password', validators=[InputRequired('Please Input Something')])