import collections
import re

import spacy

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

import textblob
from textblob import TextBlob 

from app_scripts.TextCleaner import *
from app_scripts.TextCleaner import sentiment_text_cleaner

# Text statistic helpers functions:
# - take_second
# - text_values_counts_dict
# - general_wcount_order_for_narrow_phrasegroup
# - get_str_columns_unique_values
# - elect_n_most_occuring_phrases
# - ext_sentiment
# - get_sentences_with_keyword
# - phrases_sentiment_in_respect_to_full_text

# Main functions to import: text_values_counts_dict, select_n_most_occuring_phrases, text_sentiment, get_sentences_with_keyword, phrases_sentiment_in_respect_to_full_text
stopwords = nltk.corpus.stopwords.words('english')

# Inside-a-dict helper function
def take_second(element):
	return element[1]

# Turns any text into a dictionary containint unique words and their counts.
def text_values_counts_dict(text):
	words = text.split()
	stopwords = nltk.corpus.stopwords.words('english')
	words = [w for w in text.split() if w not in stopwords]
	vc = {}
	for word in words:
		vc[word] = 0
	for word in words:
		vc[word] += 1
	vc_tuples = [(v, c) for v, c in vc.items()]
	vc_sorted = sorted(vc_tuples, key=take_second)[::-1]
	
	d = collections.OrderedDict()
	for tup in vc_sorted:
		k = tup[0]
		v = tup[1]
		d[k] = v
	return d

# Generates a wordcount for narrow phrase group inside a whole text.
def general_wcount_order_for_narrow_phrasegroup(general_wcount, phrasegroup):
	# ToDo: bi/tri-grams wcnt for longer phrases.

	new_dict = collections.OrderedDict()
	for word in phrasegroup:
		if len(word) == 1:
			if word in general_wcount:
				if not word in new_dict:
					new_dict[word] = general_wcount[word]
				else:
					new_dict[word] += general_wcount[word]
		elif len(word) > 1:
			word_temp = word.split()[0]
			if word_temp in general_wcount:
				if not word_temp in new_dict:
					new_dict[word] = general_wcount[word_temp]
				else:
					new_dict[word_temp] += general_wcount[word_temp]
	output_with_n = sorted(new_dict.items(), key=take_second)[::-1]
	output = [word_and_n[0] for word_and_n in output_with_n]
	return output # output_with_n

# Gets a all unique strings inside of a given frame column.
def get_str_columns_unique_values(df, columns_to_get):
	values_list = []
	values_indexes = []
	for i in range(len(df)):
		for c in columns_to_get:
			noun_ent_field = df.loc[i, c]
			if isinstance(noun_ent_field, str):
				if ', ' in noun_ent_field:
					noun_ent_contents = [v for v in noun_ent_field.split(', ') if v.strip()]
					values_list.extend(noun_ent_contents)
					values_indexes.append(i)
				else:
					if noun_ent_field.strip():
						values_list.append(noun_ent_field)
						values_indexes.append(i)
					
	unique_values_list = list(set(values_list))

	return unique_values_list


# Selects N most occuring prases out of a whole dataframe column.
def select_n_most_occuring_phrases(df, column_name, general_word_counts, show_n):
	all_phrases = get_str_columns_unique_values(df, [column_name])
	ordered_phrases = general_wcount_order_for_narrow_phrasegroup(general_word_counts, all_phrases)
	top_n_phrases = ordered_phrases[:show_n]
	phrases_string = ', '.join( top_n_phrases )
	return phrases_string
	#return ordered_phrases
# Returns sentimcent for a given text (whole string judgement).
def text_sentiment(text):
	text = sentiment_text_cleaner(text)
	sent_value = TextBlob(text)
	return sent_value.sentiment.polarity

# Returns list of sentences containing keywords (prequisite: 'keywords' column).
def get_sentences_with_keyword(df): # Simplify
	return [df.loc[i, 'sentence'] for i in range(len(df)) if df.loc[i, 'keywords'] ]

# Returns a dict of given phrases group inside a sentences inst containing their sentiment vaulue (-1 to 1 range)/
def phrases_sentiment_in_respect_to_full_text(sentences_list, phrases_group):
	# input: two word lists
	# output: ordered dict
	
	nlp = spacy.load('en_core_web_sm')
	kwsent_d = collections.OrderedDict()
	phrases_group = [w.lower() for w in phrases_group]
	for w in phrases_group:
		kwsent_d[w] = [0.0, 0]
		
	kwsents = []
	for ks in sentences_list:

		doc = nlp(ks)
		ks_i = [(i, w) for i, w in enumerate(doc)]
		
		for word in ks_i:
			i = word[0]
			w = word[1]
			if w.text.lower() in phrases_group:
				start = i - 3
				end = i + 3
				if start < 0:
					start = 0
				sfrac = ks.split()[start:end]
				sfracs = ' '.join(sfrac)
				sfrac_value = TextBlob(sfracs).sentiment.polarity

				kwsent_d[w.text.lower()][0] += sfrac_value
				kwsent_d[w.text.lower()][1] += 1

	for k,v in kwsent_d.items():
		sent = kwsent_d[k][0]
		num = kwsent_d[k][1]
		if num == 0:
			result = 0.0
		else:
			result = sent/num
		kwsent_d[k] = round(result,3)
	
	kwsent_d = collections.OrderedDict(sorted(kwsent_d.items(), key=take_second)[::-1])
	return kwsent_d

