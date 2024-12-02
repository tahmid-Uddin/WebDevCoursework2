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
        if field.data == None:
            raise ValidationError(message)
        
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
    #Exampl3P@ssw0rd!
    message = "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    def _ValidatePassword(form, field):
        password = field.data
        if (len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[a-z]', password) or 
            not re.search(r'\d', password) or 
            not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)): 
            raise ValidationError(message)
        

    return _ValidatePassword


def ValidateNumber():
    #Exampl3P@ssw0rd!
    message = "Number can't be negative."

    def _ValidateNumber(form, field):
        try:
            number = int(field.data)
        except:
            raise ValidationError(message)
        
        if number < 0:
            raise ValidationError(message)
        

    return _ValidateNumber


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
    address = wtforms.StringField(validators=[])


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