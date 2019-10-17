from bs4 import BeautifulSoup
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


stopwords = nltk.corpus.stopwords.words('english')
WNL = WordNetLemmatizer()

def remove_url(text):
    return re.sub('https?://[A-Za-z0-9./]+','',text)
def html_strip_praser(text):
    return BeautifulSoup(text, "html.parser").get_text()
def html_strip_lxml(text):
    return BeautifulSoup(text, 'lxml').get_text()
def remove_special_characters(text, preserve):
    return re.sub("[^a-zA-Z{}]".format(preserve), " ", text)
def lowercase_text(text):
    return text.lower()
def strip_inner_spaces(text):
    return ' '.join([w.strip() for w in text.split()])
def remove_stop_words(text):
    stopwords = nltk.corpus.stopwords.words('english')
    return ' '.join([w for w in text.split() if not w in set(stopwords)])
def lemmatize_words(text, WNL):
    WNL = WordNetLemmatizer()
    return ' '.join([WNL.lemmatize(word, pos='v') for word in text.split()])


# Bugfix:
# > single letters, 
# > empty strings 
# > fix word.strip()
def word_counts_text_cleaner(text):
    text = remove_url(text)
    #text = html_strip_lxml(text)
    text = remove_special_characters(text, preserve='-')
    text = lowercase_text(text)
    text = strip_inner_spaces(text)
    text = remove_stop_words(text)
    text = lemmatize_words(text, WNL)
    return text

def entity_recognition_text_cleaner(text):
    text = remove_url(text)
    #text = html_strip_lxml(text)
    text = remove_special_characters(text, preserve='-')
    text = strip_inner_spaces(text)
    text = remove_stop_words(text)
    return text

def sentiment_text_cleaner(text):
    text = remove_url(text)
    #text = html_strip_lxml(text)
    text = remove_special_characters(text, preserve='-')
    text = lowercase_text(text)
    text = strip_inner_spaces(text)
    text = remove_stop_words(text)
    text = lemmatize_words(text, WNL) # ?
    return text

def handy_cleaner(text):
    #text = html_strip_parser(text)
    text = remove_special_characters(text, preserve='-') # add characters
    text = remove_stop_words(text)
    #text = lowercase_text(text)
    text = strip_inner_spaces(text)
    return text

def kw_cleaner(text):
    #text = html_strip_lxml(text)
    text = remove_special_characters(text, preserve='-') # add characters
    text = remove_stop_words(text)
    text = lowercase_text(text)
    text = strip_inner_spaces(text)
    text = lemmatize_words(text, WNL) # ?
    return text

