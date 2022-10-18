import os
from . import io,grid

systems = {}
systems["Ska"] = io.read("map","Ska",grid.Grid)

def get_tile(system_name,x,y):
	system = systems[system_name]
	return system.get(x,y)
def get_all():
	return systems.keys()