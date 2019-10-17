from flask import Flask, render_template, flash, redirect, request

import os
import collections

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import re
import spacy
import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
#nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
import textblob
from textblob import TextBlob

#from forms.reader_form import ReaderForm
#from forms.keywords_form import AddKeywordsForm, RmvKeywordsForm, RmvSetForm
#from forms.comparer_form import CompareForm

from app_scripts.DataBaseManager import DataBaseManager
from app_scripts.reader_input_helpers import get_input_text
from app_scripts.TextCleaner import *
from app_scripts.TextCleaner import word_counts_text_cleaner, entity_recognition_text_cleaner, sentiment_text_cleaner, handy_cleaner, kw_cleaner
from app_scripts.TextToFrame import TextToFrame
from app_scripts.TextFeatureEngineering import TextFeatureEngineering
from app_scripts.text_statistics_helpers import text_values_counts_dict, select_n_most_occuring_phrases, text_sentiment, get_sentences_with_keyword, phrases_sentiment_in_respect_to_full_text
from app_scripts.reader_output_text_helpers import sentences_to_spanned_html, sentences_to_html
from app_scripts.PlottingTextData import plot_word_counts, plot_words_sent



app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'



# 1. INDEX.
# ---------

@app.route('/', methods=['GET', 'POST'])
def home():
    D = 'tbu'
    F = None
    return render_template('home.html', data=D, form = F)



# 2. KEYWORDS.
# ------------

from app_scripts.DataBaseManager import DataBaseManager

from random import randint
from time import strftime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

class AddKeywordsForm(Form):
	add_kwds_set_name = TextField('Set name:', validators=[validators.required()])
	add_kwds = TextField('Keywords:', validators=[validators.required()])

class RmvKeywordsForm(Form):
	rmv_kwds_set_name = TextField('Set name:', validators=[validators.required()])
	rmv_keywords = TextField('Keywords:', validators=[validators.required()])

class RmvSetForm(Form):
	rmv_set_name = TextField('Set name:', validators=[validators.required()])

#@app.route('/', methods=['GET', 'POST'])
@app.route('/keywords', methods=['GET', 'POST'])

def keywords():

	credentials = { 'dbname': 'reader_keywords', 'dbuser': 'luke'} # TEMP: into a file.
	keywords_table_name = 'keywords_test'
	keywords_columns_types = [('set_name', 'text'), ('keyword', 'text'),]
	DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)

	form_add_kw = AddKeywordsForm(request.form)
	form_rmv_kw = RmvKeywordsForm(request.form)
	form_rmv_set = RmvSetForm(request.form)

	if request.method == "POST":

		if request.form['submit'] == 'Add keywords':
			sa = request.form['add_kwds_set_name']
			ka = request.form['add_kwds']
			if form_add_kw.validate():
				flash('Added {} keywords to set {}.'.format(ka, sa))
				DBM.add_keywords(sa, ka)
			else:
				flash('Error, fields left unfilled.')

		if request.form['submit'] == 'Remove keywords':
			sr = request.form['rmv_kwds_set_name']
			kr = request.form['rmv_keywords']
			if form_rmv_kw.validate(): 
				flash('Removed {} keywords from set {}.'.format(sr, kr))
				DBM.rmv_keywords(sr, kr)
			else:
				flash('Error, fields left unfilled.')

		if request.form['submit'] == 'Remove set':
			rs = request.form['rmv_set_name']
			if form_rmv_set.validate():
				flash('Removed set {} with all keywords.'.format(rs))
				DBM.rmv_kwd_set(rs)
			else:
				flash('Error, fields left unfilled.')

	return render_template('keywords.html', form_add_kw=form_add_kw, form_rmv_kw=form_rmv_kw, form_rmv_set=form_rmv_set)



# 3. READER.
# ----------



from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired

class ReaderForm(Form):
	#link_field = TextField('Paste link or text:', validators=[validators.required()], default='https://en.wikipedia.org/wiki/Ion_(dialogue)')
	link_field = StringField('Paste link or text:', validators=[DataRequired()], default="https://en.wikipedia.org/wiki/Modularity_(biology)")
	#input_button = SubmitField('Run keyword reader.')

	credentials = { 'dbname': 'reader_keywords', 'dbuser': 'luke'} # TEMP: into a file.
	keywords_table_name = 'keywords_test'
	keywords_columns_types = [('set_name', 'text'), ('keyword', 'text'),]
	DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)
	DBM.create_table()
	#rmv_set_name = TextField('Set name:', validators=[validators.required()])

	# Keywords set
	select_choices = DBM.get_names_of_sets()
	select_choices = [(str(sc), str(sc)) for i, sc in enumerate(select_choices)]
	select_choices = [('None - pick one', 'None - pick one')] + select_choices
	select = SelectField(choices=select_choices, validators=[DataRequired()])

	# Reader options - checkbox
	nouns_display = BooleanField('Display nouns.', default=True)
	nouns_amount = IntegerField('max:', default=5)
	
	ent_display = BooleanField('Display entities.', default=True)
	ent_amount = IntegerField('max:', default=5)

	summary_display = BooleanField('Display summary.', default=True)
	graphs_display = BooleanField('Display graphs.', default=True)

	# Reader:
	reader_mode = 	[	
					('Keyword sentences', 'Keyword sentences'),
					('Keyword sentences + hints', 'Keyword sentences + hints'),
					]
	reader_mode_select = SelectField(choices=reader_mode, validators=[DataRequired()])
	


	# General options: 
	sent_score = None
	graphs = None
	show_text = None
	
	# Graphs - Multiselect
	graph_types = [('Keyword counts graph', 'Word counts graph', 'Entities graph', 'Groupped entities graph' )] 
	graph_types_select = SelectMultipleField('Select graphs to display.', choices=graph_types, validators=[DataRequired()])

	# SUBMIT
	select_button = SubmitField('Confirm your pick.')

# =========================================================================================================

@app.route('/reader', methods=['GET', 'POST'])
def reader():
	# Clean, unify later
	credentials = { 'dbname': 'reader_keywords', 'dbuser': 'luke'} # TEMP: into a file.
	keywords_table_name = 'keywords_test'
	keywords_columns_types = [('set_name', 'text'), ('keyword', 'text')]

	DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)
	DBM.create_table()

	RF = ReaderForm(request.form)

	if RF.validate():
		flash('RF validate')

	link_validation = RF.link_field.validate(RF)
	select_validation = RF.select.validate(RF)

	if RF.select_button.data is True:

		set_name = RF.select.data
		keywords = DBM.get_set_keywords(set_name)
		keywords = [k.lower() for k in keywords]
		full_text = get_input_text(RF.link_field.data)

		# Computation costs reduction - further fix.
		if RF.reader_mode_select.data == 'Keyword sentences + hints':
			READER_MODE_FRAME_TYPE = 'Full'
		# elif RF.reader_mode_select.data == 'Keyword sentences':
		# 	READER_MODE_FRAME_TYPE = 'Handy'
		else:
			READER_MODE_FRAME_TYPE = 'Full'
		
		#----------

		# Word counts
		general_word_counts = text_values_counts_dict(full_text)
		#flash(general_word_counts)
		# Full text sentiment [useless?]
		
		#full_text_sentiment = text_sentiment(full_text) # int 
		#flash(full_text_sentiment)

		# TextFrame ( future: CompCost minimalization: df types (handy, spec, lightweight)
		# - Text to sentences frame
		# - Feature Engineering
		# ---------------------

		# Frame with a raw and cleaned sentences.
		TTF = TextToFrame(full_text, keywords)
		df_sentences = TTF.prepare_sentence_dataframe()

		# Dataframe with defined features pick.
		TTE = TextFeatureEngineering(df_sentences, keywords)
		#flash(str(TTE))

		df = TTE.run('Full')
		
		# Sentences with a keyword
		keyword_sentences = get_sentences_with_keyword(df)
		#flash(keyword_sentences)
		
		# DataFrame to Results: Minimalization
		# ------------------------------------
		
		# Keywords display.
		keywords_display = ', '.join([k for k in keywords if k != ''])

		# N nouns display.
		if RF.nouns_display.data == True:
			n_nouns = RF.nouns_amount.data
			nouns = select_n_most_occuring_phrases(df, 'nouns', general_word_counts, n_nouns)
		else:
			nouns = None
		
		
		# N entities display.
		if RF.ent_display.data == True:
			n_ent = RF.ent_amount.data
			ents_org = select_n_most_occuring_phrases(df, 'ent_org', general_word_counts, n_ent)
			
			# ents org sentiment test:
			all_sentences = sent_tokenize(full_text)
			
			phrases_group = ents_org.split()
			ents_org_sent = phrases_sentiment_in_respect_to_full_text(all_sentences, phrases_group)
			#for k, v in ents_org_sent.items():
			#	print(k, v)
			ents_p = None
			ents_gpe = None
			ents_norp = None
			#ents_p = select_n_most_occuring_phrases(df, 'ent_person', general_word_counts, n_ent)
			#ents_gpe = select_n_most_occuring_phrases(df, 'ent_gpe', general_word_counts, n_ent)
			#ents_norp = select_n_most_occuring_phrases(df, 'ent_norp', general_word_counts, n_ent)
		else:
			#flash('b')
			ents_org, ents_p, ents_gpe, ents_norp = None, None, None, None



		# Display summary part.
		if RF.summary_display.data == True:
			summary_part = True
		else:
			summary_part = None

		if RF.graphs_display.data == True:
			fig1 = plot_word_counts(general_word_counts, 10)
			fig3 = plot_words_sent(ents_org_sent)
			graph_test = '/static/images/word_counts_graph_xx.png' # Recode
			graph_test3 = '/static/images/word_counts_graph_xx3.png' # Recode
			graphs = [graph_test, graph_test3]
		else:
			graphs = None

		# Render template display
		featured_sentences = []
		for i in range(len(df)):
		    idx = i
		    is_sent = df.loc[i, 'keywords']
		    words = str(df.loc[i, 'named_ents_nouns'])
		    sent = str(df.loc[i, 'sentence'])
		    featured_sentence = [idx, is_sent, words, sent]
		    featured_sentences.append(featured_sentence)
		
		#reader_frame_type_validation = RF.reader_frame_select.data
		reader_frame = RF.reader_mode_select.data
		if RF.reader_mode_select.data == 'Keyword sentences + hints':
			sentences_html = sentences_to_spanned_html(featured_sentences)
		elif RF.reader_mode_select.data == 'Keyword sentences':
			sentences_html = sentences_to_html(featured_sentences)


		return render_template('reader.html', title='Reader', spanned_test=sentences_html, reader_form=RF, summary_part=summary_part, graphs=graphs, keywords=keywords_display, ks=keyword_sentences, eo=ents_org, nn=nouns, ep=ents_p, eg=ents_gpe, en=ents_norp)
	#if select_validation and not link_validation:

	# Modify contnet according to a settings.
	return render_template('reader.html', title='Reader', reader_form=RF)

#@app.route('/reader', methods=['GET','POST'])
#def reader():
#	return 'Reader test'






# ------------------------------------------

@app.route('/f2', methods=['GET', 'POST'])
def f2():
    #
    credentials = { 'dbname': 'reader_keywords', 'dbuser': 'ubuntu'} # TEMP: into a file.
    keywords_table_name = 'keywords_test'
    keywords_columns_types = [('set_name', 'text'),('keyword', 'text'),]
    #
    DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)
    #
    D =  DBM.get_set_keywords('luke')
    # D = 'f2'
    F = None
    return render_template('f2.html', data=D, form=F)





if __name__ == "__main__":
    app.run()