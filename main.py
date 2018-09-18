from flask import Flask,render_template
import urllib.request
import json
import time
import math
import os
import geopy.distance

class Bogey:
	def __init__(self, Type, Bearing, Range, Altitude, Threat):
		self.Type = Type
		self.Bearing = Bearing
		self.Range = Range
		self.Altitude = Altitude
		self.Threat = Threat

class Player:
	def __init__(self, Name, Plane):
		self.Name = Name
		self.Plane = Plane

def calculate_initial_compass_bearing(pointA, pointB):
	lat1 = math.radians(pointA[0])
	lat2 = math.radians(pointB[0])
	diffLong = math.radians(pointB[1] - pointA[1])
	x = math.sin(diffLong) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)* math.cos(lat2) * math.cos(diffLong))
	initial_bearing = math.atan2(x, y)
	initial_bearing = math.degrees(initial_bearing)
	compass_bearing = (initial_bearing + 360) % 360
	return compass_bearing

app = Flask(__name__)

@app.route("/")
def index():
	pcount = 0
	people = []
	with urllib.request.urlopen("https://state.hoggitworld.com/") as url:
		data = json.loads(url.read().decode())
		for i in range(len(data["objects"])):
			if data["objects"][i]["Flags"]["Human"] == True:
				pcount = pcount + 1
				name = str(data["objects"][i]["UnitName"])
				plane = str(data["objects"][i]["Name"])
				people.append(Player(name, plane))
		sorted_people = sorted(people, key=lambda x: x.Name)

	return(render_template("index.html", pcount=pcount, sorted_people=sorted_people))
    

@app.route('/user/<target>')
def show_user_profile(target):
	with urllib.request.urlopen("http://state.hoggitworld.com/") as url:
		data = json.loads(url.read().decode())
		for i in range(len(data["objects"])):
			if data["objects"][i]["Flags"]["Human"] == True:
				if data["objects"][i]["UnitName"] == target:
					MyLat = data["objects"][i]["LatLongAlt"]["Lat"]
					MyLon = data["objects"][i]["LatLongAlt"]["Long"]
	unsorted_bogeys = []
	count = 0
	for i in range(len(data["objects"])):
		if data["objects"][i]["Flags"]["Human"] == False:
			if data["objects"][i]["Coalition"] == "Allies" and data["objects"][i]["Flags"]["Born"] == True:
				Type = False
				Threat = False
				if data["objects"][i]["Name"] == "Su-27":
					Type = "Su-27"
					Threat = "red"
				elif data["objects"][i]["Name"] == "F-5E-3":
					Type = "F5"
					Threat = "red"
				elif data["objects"][i]["Name"] == "Su-25T":
					Type = "Su-25T"
					Threat = "yellow"
				elif data["objects"][i]["Name"] == "Mi-26":
					Type = "Mi-26"
					Threat = "green"
				elif data["objects"][i]["Name"] == "J-11A":
					Type = "J-11A"
					Threat = "red"
				elif data["objects"][i]["Name"] == "A-50":
					Type = "A-50"
					Threat = "blue"
				elif data["objects"][i]["Name"] == "MiG-21Bis":
					Type = "MiG-21Bis"
					Threat = "red"
				elif data["objects"][i]["Name"] == "MiG-29S":
					Type = "MiG-29S"
					Threat = "red"
				elif data["objects"][i]["Name"] == "MiG-31":
					Type = "MiG-31"
					Threat = "red"

				Lat = data["objects"][i]["LatLongAlt"]["Lat"]
				Lon = data["objects"][i]["LatLongAlt"]["Long"]
				Alt = data["objects"][i]["LatLongAlt"]["Alt"]
				if Type != False and Threat != False:
					MyPos = (MyLat, MyLon)
					TPos = (Lat, Lon)
					Distance = geopy.distance.distance(MyPos,TPos).nm
					A = (MyLat, MyLon)
					B = (Lat, Lon)
					Bearing = calculate_initial_compass_bearing(A, B)
					b = Bogey(Type, Bearing, Distance, round(Alt/1000,1), Threat)
					unsorted_bogeys.append(b)
					sorted_bogeys = sorted(unsorted_bogeys, key=lambda x: x.Range)
					count = count + 1
	return(render_template("user.html", name=target, sorted_bogeys=sorted_bogeys, count=count))
    
    

if __name__ == "__main__":
	app.run()