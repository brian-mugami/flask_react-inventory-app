from flask_wtf.form import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired
class AdminRegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(message="Please input your first name..")])
    last_name = StringField("Last Name", validators=[DataRequired(message="Please input your last name..")])
    email = EmailField("email", validators=[DataRequired(message="Please input your Email.")])
    password1 = PasswordField("password", validators=[DataRequired(message="Password required")])
    password2 = PasswordField("retype-password", validators=[DataRequired(message="Password required")])
    register = SubmitField("Submit")
