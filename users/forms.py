from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    """Form for creating and editing users"""
    username = StringField('Username', 
        validators=[DataRequired(message="Username is required"), 
                    Length(min=3, max=255, message="Username must be 3-255 characters")])
    
    full_name = StringField('Full Name', 
        validators=[DataRequired(message="Full name is required"),
                    Length(min=2, max=255, message="Full name must be 2-255 characters")])
    
    email = StringField('Email', 
        validators=[DataRequired(message="Email is required"),
                    Email(message="Please enter a valid email address")])
    
    user_type = SelectField('User Type', 
        choices=[('Admin', 'Admin'), ('Normal', 'Normal')],
        default='Normal')
    
    role_id = SelectField('Role', 
        choices=[],  # Will be populated dynamically
        coerce=str,
        validators=[Optional()])
    
    is_active = BooleanField('Active', default=True)
    
    submit = SubmitField('Save')
