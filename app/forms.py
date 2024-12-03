from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

""" 
SubmitFields added to mitigate headless POST requests
https://wtforms.readthedocs.io/en/2.3.x/_modules/wtforms/fields/simple/#SubmitField
"""

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CreatePetitionForm(FlaskForm):
    title = StringField('Petition Title', validators=[DataRequired(), Length(min=3, max=32)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=3, max=1024)])
    tag_line = StringField('Tag Line', validators=[DataRequired(), Length(min=3, max=32)])
    image_url = StringField('Image URL', validators=[Length(max=128)])
    category = SelectField('Category', choices=[('Academic', 'Academic'), ('Co-Curricular', 'Co-Curricular'),
                                                ('Wellbeing', 'Wellbeing')], validators=[DataRequired()])
    submit = SubmitField('Create Petition')


class EditPetitionForm(FlaskForm):
    title = StringField('Petition Title', validators=[DataRequired(), Length(min=3, max=32)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=3, max=1024)])
    tag_line = StringField('Tag Line', validators=[DataRequired(), Length(min=3, max=32)])
    image_url = StringField('Image URL', validators=[Length(max=128)])
    status = SelectField('Status', choices=[('Closed', 'Closed'), ('Victory', 'Victory'),
                                            ('Waiting', 'Waiting')], validators=[DataRequired()])
    submit = SubmitField('Update Petition')


class EditSettingsForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=16)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=16)])
    username = StringField('Username', validators=[DataRequired(), Length(max=16)])
    about_me = TextAreaField('About Me', validators=[Length(max=256)])
    submit = SubmitField('Save')


class SignPetitionForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[Length(max=32)])
    is_anonymous = BooleanField('is_anonymous', default=False)
    submit = SubmitField('Sign this Petition')
