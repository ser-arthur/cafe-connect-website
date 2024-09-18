from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Email, EqualTo, ValidationError, NumberRange
from .data import COUNTRIES, CURRENCIES, STAR_RATINGS
from .models import User
import re


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired(), Length(min=2, max=30)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=25)])
    country = SelectField('Country', choices=COUNTRIES, validators=[DataRequired()], default='United States (US)')
    map_url = StringField('Map URL', validators=[DataRequired(), URL()])
    coffee_price = FloatField('Coffee Price', validators=[DataRequired()])
    currency = SelectField('Currency', choices=CURRENCIES, validators=[DataRequired()], default='$')
    wifi_strength = SelectField('Wifi Strength', choices=STAR_RATINGS, validators=[DataRequired()])
    seats = IntegerField('Seats', validators=[DataRequired(), NumberRange(min=0)])
    has_sockets = SelectField('Has Sockets', choices=[('True', 'Yes'), ('False', 'No')], default='False',
                              validators=[DataRequired()])
    has_toilet = SelectField('Has Toilet', choices=[('True', 'Yes'), ('False', 'No')], default='False',
                             validators=[DataRequired()])
    images = FileField('Cafe Images', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])
    full_review = TextAreaField('Full Review', validators=[Length(min=3, max=300)])
    full_rating = SelectField('Full Rating', choices=STAR_RATINGS[1:], validators=[DataRequired()])
    submit = SubmitField('Add Cafe')


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

    def validate_password(self, password):
        password_criteria = [
            (r'.{8,}', 'Password must be at least 8 characters long.'),
            (r'[a-z]', 'Password must contain at least one lowercase letter.'),
            (r'[0-9]', 'Password must contain at least one digit.'),
            (r'[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};:"\\|,.<>\/?]', 'Password must contain at least one special character.')
        ]
        for pattern, error_message in password_criteria:
            if not re.search(pattern, password.data):
                raise ValidationError(error_message)

    def create_username(self, email):
        username = email.lower().split('@')[0]
        username = re.sub(r'\W+', '', username)  # Remove non-alphanumeric characters

        count = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{count}"
            count += 1
        return username
