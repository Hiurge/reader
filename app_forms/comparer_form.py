from flask import render_template, flash, redirect, request

from wtforms import StringField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired

class CompareForm(FlaskForm):
	input_link1	= StringField('Link 1', validators=[DataRequired()])
	input_link2 = StringField('Link 2', validators=[DataRequired()])
	submit = SubmitField('Compare')
