import smtplib
from email.mime.text import MIMEText
import sqlite3
from config import EMAIL, AUTH, SERVER, CHARSET, PORT
from random import randint
from datetime import datetime
		

class Database(object):

	def __init__(self, file, _init=False):

		self.db_file = file
		self.code = lambda length: ''.join([CHARSET[randint(0, len(CHARSET) - 1)] for char in range(length)])
		self.connection = sqlite3.connect(self.db_file)
		self.cursor = self.connection.cursor()
		if _init: self._init()

	def _init(self):
		self.cursor.execute("CREATE TABLE authcodes(email text PRIMARY KEY, code text, created text)")
		self.connection.commit()

	def create_code(self, email, length=6):
		created = str(datetime.now())[0:16]
		code = self.code(length)
		values = (email, code, created)
		self.cursor.execute("SELECT * from authcodes WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is not None: return None
		self.cursor.execute("INSERT INTO authcodes VALUES(?, ?, ?)", values)
		self.connection.commit()
		return code

	def check_code(self, email, attempt):
		self.cursor.execute("SELECT * from authcodes WHERE email=?", (email,))
		fetch = self.cursor.fetchone()
		if fetch is None: return None
		if fetch[1] != attempt: return False 
		self.cursor.execute("DELETE FROM authcodes WHERE email=?", (email,))
		self.connection.commit()
		return True

class Email(object):

	def __init__(self):

		self.EMAIL = EMAIL
		self.AUTH = AUTH
		self.SERVER = SERVER
		self.smtp = smtplib.SMTP(SERVER, PORT)
		self.smtp.starttls()
		self.smtp.login(EMAIL, AUTH)

	def send_email(self, reciever, code):
		message = MIMEText('Verification Code: {}'.format(code))
		message['Subject'] = "Verification"
		message['From'] = self.EMAIL
		self.smtp.sendmail(self.EMAIL, [reciever], message.as_string())


