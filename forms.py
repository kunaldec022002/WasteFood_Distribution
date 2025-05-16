from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField
from wtforms import IntegerField, SubmitField, DateTimeField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    role = SelectField('Register as', choices=[
        ('donor', 'Food Donor (Restaurants, Grocers, Individuals)'),
        ('recipient', 'Food Recipient (Food Banks, Shelters, Individuals)')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class FoodListingForm(FlaskForm):
    title = StringField('Food Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    quantity = StringField('Quantity/Servings', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('prepared', 'Prepared Food'),
        ('produce', 'Fresh Produce'),
        ('baked', 'Bakery Items'),
        ('canned', 'Canned/Packaged'),
        ('dairy', 'Dairy Products'),
        ('meat', 'Meat/Protein'),
        ('other', 'Other')
    ])
    expiration_date = DateField('Expiration Date', validators=[DataRequired()])
    location = StringField('Pickup Location', validators=[DataRequired()])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    image = FileField('Food Image (Optional)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Create Listing')

class PickupForm(FlaskForm):
    pickup_time = DateTimeField('Preferred Pickup Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Request Pickup')

class UpdateProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    submit = SubmitField('Update Profile')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('all', 'All Categories'),
        ('prepared', 'Prepared Food'),
        ('produce', 'Fresh Produce'),
        ('baked', 'Bakery Items'),
        ('canned', 'Canned/Packaged'),
        ('dairy', 'Dairy Products'),
        ('meat', 'Meat/Protein'),
        ('other', 'Other')
    ])
    distance = SelectField('Distance', choices=[
        ('5', 'Within 5 miles'),
        ('10', 'Within 10 miles'),
        ('25', 'Within 25 miles'),
        ('50', 'Within 50 miles'),
        ('0', 'Any distance')
    ])
    submit = SubmitField('Search')
