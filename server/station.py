import os
from . import io,grid,map,items

class SItems(items.Items):
	def __init__(self,default=0,system="",**kwargs):
		super().__init__(default,**kwargs)
		self.system = ""
	def add(self,key,value):
		super().add(key,value)
		write(self.system)
	def remove(self,key):
		super().remove(key)
		write(self.system)

stations = {}
for system in map.get_all():
	stations[system] = io.read(os.path.join("station",system+".json"),grid.Grid)
	for station in stations[system].get_all():
		if "items" not in station:
			station["items"] = {}
		station["items"] = SItems(system=system,**station["items"])

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
		"items": SItems(system=system)
	}
	stations[system].set(x,y,table)
	write(system)