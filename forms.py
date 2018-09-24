from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField



# Add new post or edit exisiting post form
class AddEditPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=40, message='Title is too long.')])
    category = SelectField(u'Category', choices=[('writing', 'Writing'), ('tech', 'Tech'), ('food', 'Food'), ('video', 'Video')])
    draft = BooleanField('Draft')
    body = TextAreaField('Content Area')
    submit = SubmitField('Save Post')
    header_image = FileField('Header Image')


# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#Register Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
