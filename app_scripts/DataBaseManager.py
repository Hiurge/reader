import psycopg2

class DataBaseManager():

	# Class manages one table with given name and schema (columns/types).

	# Main used functions:
	# - add_keywords(set_name, keywords)
	# - rmv_keywords(set_name, keywords)
	# - rmv_kwd_set(set_name)
	# - get_set_keywords(set_name)
	# - get_names_of_sets()

	# Secondary/helper functions:
	# - db_do(command)
	# - create_table()
	# - drop_table()

	# Prequisites: 
	# You need a psql and a database. To create a new DB (linux ubuntu):
		# .........$ sudo -u postgres psql
		# postgres=# create database MYDB;
		# postgres=# create user MYUSER with encrypted password 'MYPASSWORD';
		# postgres=# grant all privileges on database MYDB to MYUSER;

	# Further improvements (TBD):
	# ---------------------
	# Rewrite into session handler
	# Rewrite into safe pass handler
	# Add better db exists check
	# Add - optional - user defined tables. (!)
	# Add: setter, getter
	# Reset index
	# Inmemory/db - cycle del ? out of session=del

	def __init__(self, credentials, table_name, columns_types):

		self.dbname = credentials['dbname']
		self.dbuser = credentials['dbuser']
		self.dbpswd = None
		self.dbport = None	

		self.table_name = table_name # 'table name'
		self.columns_types = columns_types # [(col, type), (...) ]

	# Executes one passed command.
	def db_do(self, command):
		try:
			self.conn = psycopg2.connect('dbname={} user={}'.format(self.dbname, self.dbuser))
			self.cur = self.conn.cursor()
			self.cur.execute(command)
			self.conn.commit()
			self.conn.close()
			self.cur.close()
		except Exception as e:
			print(e)

	# Creates a table.
	def create_table(self, ):
		columns_types = ', '.join( [ '"{}" {}'.format(tc[0], tc[1]) for tc in self.columns_types])
		command = 'CREATE TABLE IF NOT EXISTS {} ( "id" serial PRIMARY KEY, {} );'.format(self.table_name, columns_types)
		self.db_do(command)

	# Add list of keywords to the given set.
	def add_keywords(self, set_name, keywords):
		# Create table if not exists (TEMP).
		self.create_table()
		# Get existing rows.
		self.conn = psycopg2.connect('dbname={} user={}'.format(self.dbname, self.dbuser))
		self.cur = self.conn.cursor()
		columns = ', '.join(['set_name', 'keyword'])
		command = 'SELECT {} from {};'.format(columns, self.table_name)
		self.cur.execute(command)
		existing_rows = self.cur.fetchall()
		# Add unique keywords to the given set.
		
		keywords = [k.strip() for k in keywords.split(',')]
		for keyword in keywords:

			if (set_name, keyword) in existing_rows:
				continue

			columns = ', '.join([ '{}'.format(col[0]) for col in self.columns_types]) # set_name, keyword
			values  = ', '.join(["'{}'".format(set_name), "'{}'".format(keyword)]) # 'test_set', 'test_kw1'
			command = 'INSERT INTO {} ( {}) VALUES ( {});'.format(self.table_name, columns, values)
			self.db_do(command)
		self.conn.close()
		self.cur.close()

	# Remove given keywords from it's set.
	def rmv_keywords(self, set_name, keywords):
		keywords = [k.strip() for k in keywords.split(',')]
		for keyword in keywords:
			command = "DELETE FROM {} WHERE set_name = '{}' AND keyword = '{}';".format(self.table_name, set_name, keyword)
			self.db_do(command)

	# Remove a whole keywords set.
	def rmv_kwd_set(self, set_name):
		command = "DELETE FROM {} WHERE set_name = '{}'".format(self.table_name, set_name)
		self.db_do(command)

	# Drop table.
	def drop_table(self,):
		command = "DROP TABLE {}".format(self.table_name)
		self.db_do(command)

	# Get the names of all keywords.
	def get_set_keywords(self, set_name):
		self.conn = psycopg2.connect('dbname={} user={}'.format(self.dbname, self.dbuser))
		self.cur = self.conn.cursor()
		command = "SELECT keyword from {} WHERE set_name = '{}';".format(self.table_name, set_name)
		self.cur.execute(command)
		set_keywords = self.cur.fetchall()
		set_keywords = [kw[0] for kw in set_keywords]
		self.conn.close()
		self.cur.close()
		return set_keywords
	
	# Get the names of all sets.
	def get_names_of_sets(self, ):
		self.conn = psycopg2.connect('dbname={} user={}'.format(self.dbname, self.dbuser))
		self.cur = self.conn.cursor()
		command = "SELECT set_name from {};".format(self.table_name)
		self.cur.execute(command)
		all_sets_names = self.cur.fetchall()
		all_sets_names = list(set([kw[0] for kw in all_sets_names]))
		self.conn.close()
		self.cur.close()
		return all_sets_names


# Initiating:
# -----------
# credentials = { 'dbname': 'MYUSER', 'dbuser': 'MYDB'} # TEMP: into a file.
# keywords_table_name = 'keywords_test'
# keywords_columns_types = 	[
# 								#('id serial', 'PRIMARY KEY'),
# 								('set_name', 'text'),
# 								('keyword', 'text'),
# 								# ...
# 							]
# DBM = DataBaseManager(credentials, keywords_table_name, keywords_columns_types)

# Functions:
# ----------
# DBM.add_keywords(set_name, keywords)
# DBM.get_set_keywords(set_name)
# DBM.get_names_of_sets()
# DBM.rmv_keywords(set_name, keywords)
# DBM.rmv_kwd_set(set_name)
# DBM.drop_table()


# Example test (unhash Initiating):
# -------------
	
# set_name = 'test_set'
# keywords = ['test_kw1', 'test_kw2', 'test_kw3']
# DBM.add_keywords(set_name, keywords)

# DBM.rmv_keywords(set_name, keywords)
# DBM.rmv_kwd_set(set_name)
# DBM.drop_table()

# set_name = 'test_set'
# keywords = ['test_kw1', 'test_kw2', 'test_kw4']
# DBM.add_keywords(set_name, keywords)

# set_name = 'test_set2'
# keywords = ['test_kw1', 'test_kw2', 'test_kw4']
# DBM.add_keywords(set_name, keywords)

# DBM.add_keywords(set_name, keywords)
# DBM.get_set_keywords(set_name)
# DBM.get_names_of_sets()


