import os
from . import io

stations = {}
stations["Ska"] = io.read(os.path.join("station","Ska.json"))

def write(system):
	io.write(os.path.join("station",system+".json"),stations[system])
def get(system,x,y):
	x = str(x)
	y = str(y)
	if system not in stations: return
	if x not in stations[system]: return
	if y not in stations[system][x]: return
	return stations[system][x][y]
def add(system,x,y,img,owner):
	x = str(x)
	y = str(y)
	table = {
		"owner": owner,
		"image": img,
		"system": system,
		"x": x,
		"y": y,
		"items": {}
	}
	if get(system,x,y): return
	if system not in stations:
		stations[system] = {}
	if x not in stations[system]:
		stations[system][x] = {}
	if y not in stations[system][x]:
		stations[system][x][y] = table
		write(system)