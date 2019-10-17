# Reader output sentences html generator.
# - Generates flask html out of sentences list.

# Main functions to import: sentences_to_spanned_html(featured_sentences), sentences_to_html(featured_sentences)

# Generates spanned sentences display on reader part.
def sentences_to_spanned_html(featured_sentences):
	sent_part_html = '''
	'''
	style_part = '''
	'''
	for s_items in featured_sentences:
		print(s_items)
		idx = s_items[0]
		is_sent = s_items[1]
		words = s_items[2].lower() # string assumption (a, b, c) 
		sentence = s_items[3]

		str_idx = str(idx)+'.'

		if is_sent != '':
			# Generates non-spanned sentence.
			sent_html = '<p><font size="4">{:<3} {}</p>'.format(str_idx, sentence)
			sent_part_html += sent_html
		else:
			dots = 'dots_{}'.format(idx)
			dots_part = '''<span id="{}"></span>'''.format(dots)
			sent_part_html += dots_part

			# Generates sentence span placeholder.
			span_id = 'span_'+ str(idx)
			button_id = 'button_' + str(idx)
			span_words = '{:<3} {}'.format(str_idx, words) 
			onclick_scheme = '''<p onclick="spanIt('{}','{}','{}', '{}')" id="{}"><font size="2">{} (click to show)</p>'''
			onclick_html = onclick_scheme.format(span_id, button_id, span_words, dots, button_id, span_words)
			sent_part_html += onclick_html
			
			# Generates sentence span contents.
			span_scheme = '<span id="{}"><font size="4">{}. {}</span>'
			sent_span = span_scheme.format(span_id, idx, sentence)
			sent_part_html += sent_span

			style_part_scheme = '    #span_{} {{display: none;}}'.format(idx)
			style_part += style_part_scheme

	style_part = '<style>{}</style>'.format(style_part)

	full_sent_html = sent_part_html + style_part
	return full_sent_html

# Generates keyword sentences display on reader part.
def sentences_to_html(featured_sentences):
	sent_part_html = '''
	'''
	style_part = '''
	'''
	for s_items in featured_sentences:
		print(s_items)
		idx = s_items[0]
		is_sent = s_items[1]
		words = s_items[2].lower() # string assumption (a, b, c) 
		sentence = s_items[3]

		str_idx = str(idx)+'.'

		if is_sent != '':
			sent_html = '<p class="keyword_sentence_k"><font size="4">{:<3} {}</p>'.format(str_idx, sentence)
			sent_part_html += sent_html

	style_part = '<style>{}</style>'.format(style_part)

	full_sent_html = sent_part_html + style_part
	return full_sent_html
