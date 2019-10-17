import urllib.request, urllib.parse, urllib.error 
from bs4 import BeautifulSoup
import re

# Reader input helpers:
# - Turns reader input into one string text contents weather its a link contents or a pasted text.

# Main function to import: get_input_text(contents)


# Gets website contents and turns into list of paragraphs (sentences).
def url_to_txt(url):
	html = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(html, 'html.parser') # "lxml")
	sentences = soup.find_all('p')
	sentences = [s.get_text() for s in sentences if s]
	return sentences

# Decides if reader input string is a link or pure text to be taken as a contents.
def url_or_text(input_string):
	if ' ' in input_string:
		return 'text'
	else:
		try:
			link = re.search("(?P<url>https?://[^\s]+)", input_string).group("url")
			return 'link'
		except:
			try:
				link = re.search("(?P<url>www.[^\s]+)", input_string).group("url")
				return 'link'
			except:
				return 'text'

# Turns link contents into one string of text.
def get_input_text(contents):
	if url_or_text(contents) == 'link':
		link = contents
		list_of_p = url_to_txt(link)
		full_text = ' '.join(list_of_p)
		return full_text
	else:
		full_text = contents
		return full_text

