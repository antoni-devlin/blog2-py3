from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


# Form for adding new posts
class AddEditPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField(u'Category', choices=[('video', 'Video'), ('tech', 'Tech'), ('food', 'Food'), ('writing', 'Writing')])
    draft = BooleanField('Draft')
    body = CKEditorField('Content Area')
    submit = SubmitField('Save Post')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')
    #
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')
