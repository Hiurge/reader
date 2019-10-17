from flask import render_template, flash, redirect, request
#from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CompareForm(Form):
        input_link1 = StringField('Link 1', validators=[DataRequired()])
        input_link2 = StringField('Link 2', validators=[DataRequired()])
        submit = SubmitField('Compare')
