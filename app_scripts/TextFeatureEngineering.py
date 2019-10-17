import pandas as pd

import spacy
import nltk
from nltk.tokenize import sent_tokenize

from app_scripts.TextCleaner import *
from app_scripts.TextCleaner import word_counts_text_cleaner, entity_recognition_text_cleaner, sentiment_text_cleaner, handy_cleaner, kw_cleaner

import textblob
from textblob import TextBlob 


# Generates all text features INSIDE A FRAME(!).
# - Contains separate run(self, mode) function to load simplified or specifiead mode to lower computation costs.

# General fix into:
# - add None/empty closures (!)



class TextFeatureEngineering():

	def __init__(self, df, keywords):
		self.keywords = keywords # [?]
		self.nlp = spacy.load('en_core_web_sm', parser=False)
		self.df = df # Current object

	def sentence_keywords_as_a_feature(self, one_sentence, keywords):
		one_sentence = kw_cleaner(one_sentence)
		words = one_sentence.split()
		keywords_within = [w for w in words if w in keywords]
		keywords_within = ', '.join(keywords_within)
		return keywords_within

	# Features
	# --------

	# One hot encoding for given list of phrases.
	def one_hot_encoding(self, df, phrases):
		for k in phrases:
			df[k] = 0

		for i in range(len(df)):
			for k in phrases:
				sent = df.loc[i, 'clean_sentences']
				if k in sent.split():
					df.loc[i, k] += 1
		return df

	# Lexical text properties.
	def text_ents_org(self, text):
		return ', '.join([w.text for w in self.nlp(str(text)).ents if w.label_ == 'ORG'])
	def text_ents_person(self, text):
		persons = ', '.join([w.text for w in self.nlp(str(text)).ents if w.label_ == 'PERSON'])
		return  persons
	def text_ents_gpe(self, text):
		return ', '.join([w.text for w in self.nlp(str(text)).ents if w.label_ == 'GPE'])
	def text_ents_norp(self, text):
		return ', '.join([w.text for w in self.nlp(str(text)).ents if w.label_ == 'NORP'])
	def text_dependencies(self, text):
		return ', '.join(['('+w.text+' '+w.dep_+')' for w in self.nlp(str(text))])
	def text_nouns(self, text):
		return ', '.join([w.text for w in self.nlp(str(text)) if w.pos_ == 'NOUN'])

	# Sentiment score.
	def text_sentiment(self, text):
		text = sentiment_text_cleaner(text)
		sent_value = TextBlob(text)
		return sent_value.sentiment.polarity


	# Helpers
	# -------

	def clean_multistring_separators(self, text):
		words_out = []
		for text_part in text.split('|'):
			clean_parts = [word.strip() for word in text_part.split(',') if not word == '']
			words_out.extend(clean_parts)
		words_out = list(set(words_out))
		words_out = ', '.join(words_out)
		return words_out


	# Frame types 
	# -----------

	def sentence_df_handy_mode(self):
		self.df = self.df.copy(deep=True)
		self.df['clean_sentences'] = self.df['sentence'].apply(handy_cleaner)
			
		# Add features ...
		return self.df

	def sentence_df_full_mode(self):
		df = self.df.copy(deep=True)
		xd = 'fofofof'
		### Clean sentences.
		df['clean_sentences'] = df['sentence'].apply(handy_cleaner)

		### Features

		# Keywords list feature.
		df['keywords'] = df.clean_sentences.apply(self.sentence_keywords_as_a_feature, keywords=self.keywords)

		# One hot encoded keywords.
		df = self.one_hot_encoding(df, phrases=self.keywords)

		# Parts of speach.
		df['nouns'] = df.clean_sentences.apply(self.text_nouns)

		# Entities.
		df['ent_org'] = df.clean_sentences.apply(self.text_ents_org)
		df['ent_person'] = df.clean_sentences.apply(self.text_ents_person)
		df['ent_gpe'] = df.clean_sentences.apply(self.text_ents_gpe)
		df['ent_norp'] = df.clean_sentences.apply(self.text_ents_norp)

		# Entities + Nouns list as a one feature.
		df['named_ents_nouns'] = df[['nouns', 'ent_org', 'ent_person', 'ent_gpe', 'ent_norp']].apply(lambda x: '|'.join(x), axis=1)
		df['named_ents_nouns'] = df['named_ents_nouns'].apply(self.clean_multistring_separators)

		# Sentiment for each of sentences. [what for?]
		df['sent_senti'] = df.clean_sentences.apply(self.text_sentiment)

		# Inner sentence dependencies.
		df['deps'] = df.clean_sentences.apply(self.text_dependencies)

		# Save frame as a CSV file.
		df.to_csv('text_full_table_development.csv', encoding='utf-8', index=None)

		# Set frame as a main object.
		self.df = df.copy(deep=True)

	def run(self, mode):
		if mode == 'Full':
			#return mode
			self.sentence_df_full_mode()
			return self.df #'x' # self.df
		elif mode == 'Handy':
			self.sentence_df_handy_mode()
		else:
			return 'else'
