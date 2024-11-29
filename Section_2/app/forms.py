from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired, ValidationError
import re 


def ValidateFirstName():
    message = "Name contains invalid characters."

    def _ValidateModuleCode(form, field):
        if not re.match(r'^[A-Za-z\s]+$', field.data):
            raise ValidationError(message)
        
    return _ValidateModuleCode

def ValidateLastName():
    message = "Name contains invalid characters."

    def _ValidateModuleCode(form, field):
        if not re.match(r'^[A-Za-z\s]+$', field.data):
            raise ValidationError(message)
        
        if len(field.data.split(" ")) != 1:
            raise ValidationError(message)
        
    return _ValidateModuleCode
#Exampl3P@ssw0rd!

def ValidatePassword():
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

class SignUpForm(FlaskForm):
    firstName = wtforms.TextAreaField(validators=[DataRequired(), ValidateFirstName()])
    lastName = wtforms.TextAreaField(validators=[DataRequired(), ValidateLastName()])
    email = wtforms.TextAreaField(validators=[DataRequired()])
    password = wtforms.TextAreaField(validators=[DataRequired(), ValidatePassword()])
    
class LoginForm(FlaskForm):
    email = wtforms.TextAreaField(validators=[DataRequired()])
    password = wtforms.TextAreaField(validators=[DataRequired()])

