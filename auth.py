import sqlite3
from crypto import hash_
from datetime import datetime
from config import CHARSET
from random import randint

class Authentication(object):

	def __init__(self, file, _init=False):

		self.db_file = file
		self.code = lambda length: ''.join([CHARSET[randint(0, len(CHARSET) - 1)] for char in range(length)])
		self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
		self.cursor = self.connection.cursor()
		if _init: self._init()

	def _init(self):
		self.cursor.execute("CREATE TABLE drivers(username text PRIMARY KEY, password text, bus text)")
		self.cursor.execute("CREATE TABLE users(email text PRIMARY KEY, password text, normal_bus text, verified boolean, signed boolean)")
		self.cursor.execute("CREATE TABLE authcodes(email text PRIMARY KEY, code text, created text)")
		self.connection.commit()

	def register(self, email, password, normal_bus, length=6):
		values = (email, hash_(password), normal_bus, False, False)
		self.cursor.execute("SELECT * from users WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is not None: return False
		self.cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?)", values)
		self.connection.commit()
		created = str(datetime.now())[0:16]
		code = self.code(length)
		values = (email, code, created)
		self.cursor.execute("SELECT * from authcodes WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is not None: return None
		self.cursor.execute("INSERT INTO authcodes VALUES(?, ?, ?)", values)
		self.connection.commit()
		return code

	def check(self, email, attempt):
		self.cursor.execute("SELECT password from users WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is None: return None
		if hash_(attempt) == fetch[0]: return True
		return False

	def verify_status(self, email):
		self.cursor.execute("SELECT verified from users WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is None: return None
		return bool(fetch[0])

	def verify(self, email, attempt):
		self.cursor.execute("SELECT * from authcodes WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is None: return None
		if fetch[1] != attempt: return False 
		self.cursor.execute("DELETE FROM authcodes WHERE email=?", (email,))
		self.connection.commit()
		self.cursor.execute("UPDATE users SET verified = 1 WHERE email=?", (email,))
		self.connection.commit()
		return True

	def normal_bus(self, email):
		self.cursor.execute("SELECT normal_bus FROM users WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		return fetch[0]
	