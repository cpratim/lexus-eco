from flask import Flask, render_template, session, redirect, url_for, request
from auth import Authentication
from mail import MailServer
from logistics import Logistics
from routes import Routes
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lolxd'
auth = Authentication('auth.db')
mail = MailServer()
routes = Routes('bus_data.json')
logistics = Logistics('logistics.db')

@app.route('/')
def index():
	if 'logged_in' in session:
		if session['logged_in'] is True: 
			return redirect(url_for('today'))
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if 'logged_in' in session:
		if session['logged_in'] is True: 
			return redirect(url_for('index'))
	from forms import RegisterForm
	register_form = RegisterForm()
	if register_form.validate_on_submit():
		email = register_form.email.data
		password = register_form.password.data
		normal_bus = register_form.normal_bus.data
		status = auth.register(email, password, normal_bus)
		if status is False:
			messages = ['Email Address ({}) Already Taken'.format(email)]
			return render_template('register.html', register_form=register_form, messages=messages, alert_type='danger')
		session['email'] = email
		code = status
		mail.send_mail(email, code)
		return redirect(url_for('verify'))
	return render_template('register.html', register_form=register_form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
	if 'email' not in session: return redirect(url_for('register'))
	email = session['email']
	if 'logged_in' in session: return redirect(url_for('index'))
	if auth.verify_status(email) is True: return redirect(url_for('index'))
	from forms import VerifyForm
	verify_form = VerifyForm()
	if verify_form.validate_on_submit():
		code = verify_form.code.data
		status = auth.verify(email, code)
		if status is False:
			messages = ['Incorrect Code Try Again']
			return render_template('verify.html', verify_form=verify_form, messages=messages, alert_type='danger')
		session['just_verified'] = True
		return redirect(url_for('login'))
	return render_template('verify.html', verify_form=verify_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'logged_in' in session: return redirect(url_for('index'))
	if 'email' in session:
		if auth.verify_status('email') is False: return redirect(url_for('verify'))
	from forms import LoginForm
	login_form = LoginForm()
	if login_form.validate_on_submit():
		email = login_form.email.data
		password = login_form.password.data
		status = auth.check(email, password)
		if status is False:
			messages = ['Incorrect Email or Password']
			return render_template('login.html', login_form=login_form, messages=messages, alert_type='danger')
		if status is None:
			messages = ['Account Doesnt Exist']
			return render_template('login.html', login_form=login_form, messages=messages, alert_type='danger')
		session['logged_in'] = True
		session['email'] = email
		session['just_logged_in'] = True
		return redirect(url_for('today'))
	if 'just_verified' in session:
		if session['just_verified'] is True:
			messages = ['Email Successfully Verified, Please Log In']
			session.pop('just_verified')
			return render_template('login.html', login_form=login_form, messages=messages, alert_type='success')
	return render_template('login.html', login_form=login_form)

@app.route('/bus/<string:number>')
def bus(number):
	from random import randint
	stops = routes.get_stops(number)
	counts = logistics.get_counts(number)
	return render_template('bus.html', stops=stops, bus_number=number, counts=counts)

@app.route('/today')
def today():
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login'))
	if logistics.reserved(session['email']) is True:
		bus, stop = logistics.get_reservation(session['email'])
		time, location = routes.get_stop_data(bus, stop)
		return render_template('reserved.html', bus=bus, stop=stop, time=time, location=location)
	normal_bus = auth.normal_bus(session['email'])
	stops = routes.get_stops(normal_bus)
	date = str(datetime.now())[0:16]
	left, right = routes.split(stops)
	if 'just_removed' in session:
		messages = ['Reservation Successfully Removed, Add a new One!']
		session.pop('just_removed')
		return render_template('today.html', left=left, right=right, date=date, normal_bus=normal_bus, messages=messages)
	if 'just_logged_in' in session:
		messages = ['Logged In Successfully. Reserve a Stop']
		session.pop('just_logged_in')
		return render_template('today.html', left=left, right=right, date=date, normal_bus=normal_bus, messages=messages)
	return render_template('today.html', left=left, right=right, date=date, normal_bus=normal_bus)

@app.route('/today/<string:number>')
def today_specific(number):
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login'))
	if logistics.reserved(session['email']) is True:
		return redirect(url_for('today'))
	stops = routes.get_stops(number)
	date = str(datetime.now())[0:16]
	left, right = routes.split(stops)
	return render_template('today.html', left=left, right=right, date=date, normal_bus=number)

@app.route('/change')
def change():
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login'))
	if logistics.reserved(session['email']) is False: return redirect(url_for('today')) 

@app.route('/remove')
def remove():
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login'))
	if logistics.reserved(session['email']) is False: return redirect(url_for('today'))
	status = logistics.remove_reservation(session['email'])
	if status is True: 
		session['just_removed'] = True
		return redirect(url_for('today'))
	return redirect(url_for('today'))

@app.route('/busses')
def busses():
	busses = routes.get_busses()
	return render_template('busses.html', busses=busses)

@app.route('/reserve')
def reserve():
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login'))
	if logistics.reserved(session['email']) is True: return render_template("reserved.html")
	bus = request.args.get('bus')
	stop = request.args.get('stop')
	email = session['email']
	status = logistics.add_stop(bus, stop, email)
	return redirect(url_for('today'))

@app.route('/logout')
def logout():
	if 'logged_in' not in session: return redirect(url_for('login'))
	if session['logged_in'] is False: return redirect(url_for('login')) 
	keys = [key for key in session]
	for key in keys: session.pop(key)
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run()