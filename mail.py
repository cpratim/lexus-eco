import smtplib
from email.mime.text import MIMEText
from config import EMAIL, AUTH, SERVER, CHARSET, PORT

class MailServer(object):

	def __init__(self):

		self.EMAIL = EMAIL
		self.AUTH = AUTH
		self.SERVER = SERVER
		self.smtp = smtplib.SMTP(SERVER, PORT)
		self.smtp.starttls()
		self.smtp.login(EMAIL, AUTH)

	def send_mail(self, reciever, code):
		message = MIMEText('Verification Code: {}'.format(code))
		message['Subject'] = "Verification"
		message['From'] = self.EMAIL
		self.smtp.sendmail(self.EMAIL, [reciever], message.as_string())