import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# PLOTS
# ==========================================================================
# Bugfix: graph size, unstability [ N records stablizer as a var]
# Labelki na bar'ach
# DELETE grafu (po przeladowaniu strony ?)
def plot_word_counts(word_counts_dictionary, top_n_records):
	sorted_values = sorted((value,key) for (key,value) in word_counts_dictionary.items())[::-1]
	x_list = [v[0] for v in sorted_values][:top_n_records]
	y_list = [v[1] for v in sorted_values][:top_n_records]
	sns.set(rc={'figure.figsize':(6,6)})
	plt.figure()
	plt.rcParams["ytick.labelsize"] = 7
	ax = sns.barplot(x=x_list, y=y_list)

	#path = '/home/luke/PythonDS_sketches/flask_template/app/static/images'
	plot_name = 'word_counts_graph_xx.png'
	plot_folder = os.getcwd() #  '/static/images'
	plot_path = plot_folder  + '/static/images/' + plot_name
	print('save fig path:', plot_path)
	plt.savefig(plot_path)
	plot, fig = None, None
	return fig

def plot_words_sent(words_sent_dict):
	sorted_values = [(value, key) for (key,value) in words_sent_dict.items()]
	print(sorted_values)
	x_list = [v[0] for v in sorted_values]
	y_list = [v[1] for v in sorted_values]
	sns.set(rc={'figure.figsize':(6,6)})

	plt.figure()
	plt.rcParams["ytick.labelsize"] = 7
	ax = sns.barplot(x=x_list, y=y_list)
	#fig = fig.get_figure()
	plot_name = 'word_counts_graph_xx3.png'
	plot_folder = os.getcwd() #  '/static/images'
	plot_path = plot_folder  + '/static/images/' + plot_name
	plt.savefig(plot_path)
	plot, fig = None, None
	return fig
# ===========================================================================

