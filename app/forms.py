from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

""" 
SubmitFields added to mitigate headless POST requests
https://wtforms.readthedocs.io/en/2.3.x/_modules/wtforms/fields/simple/#SubmitField
"""

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CreatePetitionForm(FlaskForm):
    title = StringField('Petition Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tag_line = StringField('Tag Line', validators=[DataRequired()])
    image_url = StringField('Image URL')
    category = SelectField('Category', choices=[('Academic', 'Academic'), ('Co-Curricular', 'Co-Curricular'),
                                                ('Wellbeing', 'Wellbeing')], validators=[DataRequired()])
    submit = SubmitField('Create Petition')


class EditPetitionForm(FlaskForm):
    title = StringField('Petition Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tag_line = StringField('Tag Line', validators=[DataRequired()])
    image_url = StringField('Image URL')
    status = SelectField('Status', choices=[('Closed', 'Closed'), ('Victory', 'Victory'),
                                            ('Waiting', 'Waiting')], validators=[DataRequired()])
    submit = SubmitField('Update Petition')


class EditSettingsForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    about_me = TextAreaField('About Me', validators=[Length(max=200)])
    submit = SubmitField('Save')


class SignPetitionForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Sign this Petition')
