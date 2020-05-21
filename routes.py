from config import EMAIL, AUTH, SERVER, CHARSET, PORT
import json

def read_data(file):
	with open(file, 'r') as data_file:
		data = json.load(data_file)
		return data

def dump_data(file, data):
	with open(file, 'w') as data_file:
		json.dump(data, data_file, indent=4)


class Routes(object):

	def __init__(self, file, _init=False):

		self.json_file = file
		self.data = read_data(self.json_file)

	def get_stops(self, bus_number):
		bus_number = str(bus_number)
		stops = self.data[bus_number]
		return stops

	def get_data(self):
		data = {}
		for route in self.data:
			stops = [key for key in self.data[route]]
			insert = ""
			for stop in stops:
				insert += '{}:0|'.format(stop)
			data[route] = insert
		return data

	def get_busses(self):
		ret = {}
		for key in self.data:
			ret[key] = self.data[key]["A"]
		return ret

	def get_stop_data(self, bus, stop):
		time, location = self.data[bus][stop]
		return time, location

	def split(self, stops):
		left = {}
		right = {}
		count = 0;
		for stop in stops:
			if count % 2 == 0:
				left[stop] = stops[stop]
			else:
				right[stop] = stops[stop]
			count += 1
		return left, right

