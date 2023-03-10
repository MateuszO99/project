from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from project.models import User


class SearchForm(FlaskForm):
    search_user = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"placeholder": "Search Player"}
    )
    submit_username = SubmitField("Search Player")


class SearchChampionForm(FlaskForm):
    search_champion = StringField(
        "Champion",
        validators=[DataRequired()],
        render_kw={"placeholder": "Search Champion"}
    )
    submit_champion = SubmitField("Search Champion")


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken already! Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
