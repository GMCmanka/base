from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class RoleForm(FlaskForm):
    """Form for creating and editing roles"""
    name = StringField('Role Name', 
        validators=[DataRequired(message="Role name is required"),
                    Length(min=2, max=50, message="Role name must be 2-50 characters")])
    
    submit = SubmitField('Save')
