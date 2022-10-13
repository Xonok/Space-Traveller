import os
from . import io,grid

io.check_dir("map")

systems = {}
systems["Ska"] = io.read(os.path.join("map","Ska.json"),grid.Grid)

def get_tile(system_name,x,y):
	system = systems[system_name]
	return system.get(x,y)
