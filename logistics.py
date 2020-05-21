import sqlite3
from routes import Routes

class Logistics(object):

	def __init__(self, file, _init=False):

		self.db_file = file
		self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
		self.cursor = self.connection.cursor()
		self.routes = Routes('bus_data.json')
		if _init: self._init()

	def _init(self):
		self.cursor.execute("CREATE TABLE routes(bus_number text PRIMARY KEY, stops text)")
		self.cursor.execute("CREATE TABLE students(email text PRIMARY KEY, bus text, stop text)")
		data = self.routes.get_data()
		for stop in data:
			self.cursor.execute('INSERT INTO routes VALUES(?, ?)', (stop, data[stop]))
		self.connection.commit()

	def get_stops(self, bus):
		self.cursor.execute("SELECT stops FROM routes WHERE bus_number=?", (bus, ))
		fetch = self.cursor.fetchone()[0]
		stops = {}
		for stop in fetch.split('|')[:-1]:
			stops[stop.split(':')[0]] = int(stop.split(':')[1])
		return stops

	def add_stop(self, bus, stop, email):
		if self.reserved(email) is True: return None
		stops = self.get_stops(bus)
		stops[stop] += 1
		insert = ""
		for s in stops:
			insert += "{}:{}|".format(s, stops[s])
		self.cursor.execute("UPDATE routes SET stops=? WHERE bus_number=?", (insert, bus))
		self.cursor.execute("INSERT INTO students VALUES(?, ?, ?)", (email, bus, stop))
		self.connection.commit()
		return True

	def get_counts(self, bus):
		self.cursor.execute("SELECT stops FROM routes WHERE bus_number=?", (bus, ))
		fetch = self.cursor.fetchone()[0]
		counts = {}
		for i in fetch.split('|')[:-1]:
			cx = i.split(':')
			counts[cx[0]] = int(cx[1])
		return counts

	def reserved(self, email):
		self.cursor.execute("SELECT * FROM students WHERE email=?", (email, ))
		fetch = self.cursor.fetchone()
		if fetch is None: return False
		return True

	def get_reservation(self, email):
		self.cursor.execute("SELECT * FROM students WHERE email=?", (email, ))
		fetch = self.cursor.fetchone()
		if fetch is None: return None
		return fetch[1], fetch[2]

	def clear(self):
		data = self.routes.get_data()
		for stop in data:
			self.cursor.execute('UPDATE routes SET stops=? WHERE bus_number=?', (data[stop], stop))
		self.connection.commit()

	def remove_reservation(self, email):
		bus, stop = self.get_reservation(email)
		self.cursor.execute('DELETE FROM students WHERE email=?', (email, ))
		counts = self.get_counts(bus)
		counts[stop] -= 1
		insert = ''
		for count in counts:
			insert += '{}:{}|'.format(count, counts[count])
		self.cursor.execute("UPDATE routes SET stops=? WHERE bus_number=?", (insert, bus))
		self.connection.commit() 
		return True

