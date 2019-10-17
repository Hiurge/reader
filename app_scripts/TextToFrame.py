import pandas as pd

import spacy
import nltk
from nltk.tokenize import sent_tokenize

import textblob
from textblob import TextBlob 

from app_scripts.TextCleaner import word_counts_text_cleaner, entity_recognition_text_cleaner, sentiment_text_cleaner, handy_cleaner, kw_cleaner

# Returns text (class is initiated with) into a dataframe of sentences.  

# General fix into:
# - NONE/empty closures (!!!! !)


class TextToFrame():

	def __init__(self, text, keywords):
		self.text = text
		self.keywords = keywords # [?]
		self.sentences = None
		self.df_sentences = None # Just a sentences

	# Turns a string of text into a list of sentences.
	def text_to_sentences(self):
		self.sentences = sent_tokenize(self.text)

	# Turns a list of sentences into a dataframe of sentences.
	def sentences_to_dataframe(self):
		self.df_sentences = pd.DataFrame(self.sentences, columns=['sentence'])

	# Returns text (class is initiated with) into a dataframe of sentences.  
	def prepare_sentence_dataframe(self):
		self.text_to_sentences()
		self.sentences_to_dataframe()
		return self.df_sentences

