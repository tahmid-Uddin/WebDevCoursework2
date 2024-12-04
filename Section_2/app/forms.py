from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
import wtforms
from wtforms.validators import DataRequired, ValidationError
import re 
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type


def ValidateFirstName():
    message = "Name contains invalid characters."

    def _ValidateFirstName(form, field):
        if field.data:
            #No numbers or punctuation in name
            if not re.match(r"^[A-Za-z\s]+$", field.data):
                raise ValidationError(message)
        
    return _ValidateFirstName


def ValidateLastName():
    message = "Name contains invalid characters."

    def _ValidateLastName(form, field):
        #No numbers or punctuation in name
        if not re.match(r"^[A-Za-z\s]+$", field.data):
            raise ValidationError(message)
        
        #Last name can only be one word
        if len(field.data.split(" ")) != 1:
            raise ValidationError(message)
        
    return _ValidateLastName


def ValidatePhoneNumber():
    message = "Invalid Phone number - must include country code."

    def _ValidatePhoneNumber(form, field):
        if field.data:
            number = field.data.strip()
            #Country code given - phonenumbers.parse doesn't work on numbers without country code
            if number[0] == "+":
                #Checks if the rest of the phone number contains only numbers
                try:
                    number_int = int(number[1:])
                except:
                    raise ValidationError(message)
                
                if not carrier._is_mobile(number_type(phonenumbers.parse(number))):
                    raise ValidationError(message)
            else:
                raise ValidationError(message)
    
    return _ValidatePhoneNumber


def ValidatePassword():
    message = "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    def _ValidatePassword(form, field):
        password = field.data
        #Password to have atlest one uppercase letter, one lowercase letter, one number, and one special character
        #and be more than 7 characters long
        if (len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[a-z]', password) or 
            not re.search(r'\d', password) or 
            not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)): 
            raise ValidationError(message)
        
    return _ValidatePassword


def ValidateNumber():
    message = "Invalid number entered."

    def _ValidateNumber(form, field):
        try:
            number = int(field.data)
        except:
            raise ValidationError(message)
        
        if number < 0:
            raise ValidationError(message)
        

    return _ValidateNumber


def ValidatePostCodeSupplied():
    message = "Need to include post code."

    def _ValidatePostCodeSupplied(form, field):
        # Check if address is provided (not empty after stripping whitespace)
        # No errors raised if empty, as address is optional
        if field.data and field.data.strip():
            # Can't have an address without postcode
            if not form.postCode.data or not form.postCode.data.strip():
                raise ValidationError(message)
    
    return _ValidatePostCodeSupplied


def ValidatePostCode():
    message = "Invalid postcode."

    def _ValidatePostCode(form, field):
        if field.data:
            # Can't have more than 2 parts in the postcode
            if len(field.data.split(" ")) > 2:
                raise ValidationError(message)
            
            # Longest postcode is 8 characters in the UK
            if len(field.data) > 8:
                raise ValidationError(message)
            
            # All postcodes have to be alphanumeric
            postcode = field.data.split(" ")
            for section in postcode:
                if not re.match(r'^[a-zA-Z0-9]+$', section):
                    raise ValidationError(message)
        
    return _ValidatePostCode


class SignUpForm(FlaskForm):
    firstName = wtforms.StringField(validators=[DataRequired(), ValidateFirstName()])
    lastName = wtforms.StringField(validators=[DataRequired(), ValidateLastName()])
    email = wtforms.StringField(validators=[DataRequired()])
    password = wtforms.StringField(validators=[DataRequired(), ValidatePassword()])
    
    
class LoginForm(FlaskForm):
    email = wtforms.StringField(validators=[DataRequired()])
    password = wtforms.StringField(validators=[DataRequired()])


class UpdateUserForm(FlaskForm):
    firstName = wtforms.StringField(validators=[DataRequired(), ValidateFirstName()])
    middleName = wtforms.StringField(validators=[ValidateFirstName()])
    lastName = wtforms.StringField(validators=[DataRequired(), ValidateLastName()])
    phoneNumber = wtforms.StringField(validators=[ValidatePhoneNumber()])
    email = wtforms.StringField(validators=[DataRequired()])
    address = wtforms.StringField(validators=[ValidatePostCodeSupplied()])
    postCode = wtforms.StringField(validators=[ValidatePostCode()])
    
    
class ConfirmDeliveryDetailsForm(FlaskForm):
    firstName = wtforms.StringField(validators=[DataRequired(), ValidateFirstName()])
    middleName = wtforms.StringField(validators=[ValidateFirstName()])
    lastName = wtforms.StringField(validators=[DataRequired(), ValidateLastName()])
    phoneNumber = wtforms.StringField(validators=[DataRequired(), ValidatePhoneNumber()])
    email = wtforms.StringField(validators=[DataRequired()])
    address = wtforms.StringField(validators=[DataRequired(), ValidatePostCodeSupplied()])
    postCode = wtforms.StringField(validators=[DataRequired(), ValidatePostCode()])


class SellerRegistrationForm(FlaskForm):
    businessName = wtforms.StringField(validators=[DataRequired()])
    businessPhone = wtforms.StringField(validators=[DataRequired(), ValidatePhoneNumber()])
    businessEmail = wtforms.StringField(validators=[DataRequired()])
    businessAddress = wtforms.StringField(validators=[DataRequired()])
    country = wtforms.StringField(validators=[DataRequired()])


class CreateListingForm(FlaskForm):
    name = wtforms.StringField(validators=[DataRequired()])
    description = wtforms.TextAreaField(validators=[DataRequired()])
    stock = wtforms.IntegerField(validators=[DataRequired(), ValidateNumber()])
    price = wtforms.FloatField(validators=[DataRequired(), ValidateNumber()])
    category = wtforms.StringField(validators=[DataRequired()])
    image = FileField("Product Images", validators=[FileAllowed(["jpg", "png", "jpeg"])])