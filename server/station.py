import os
from . import io,grid

stations = {}
stations["Ska"] = io.read(os.path.join("station","Ska.json"),grid.Grid)

def write(system):
	io.write(os.path.join("station",system+".json"),stations[system])
def get(system,x,y):
	return stations[system].get(x,y)
def add(system,x,y,img,owner):
	if len(stations[system].get(x,y)):
		return
	table = {
		"owner": owner,
		"image": img,
		"system": system,
		"x": x,
		"y": y,
		"items": {}
	}
	stations[system].set(x,y,table)
	write(system)