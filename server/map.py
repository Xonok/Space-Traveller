import os
from . import io

io.check_dir("map")

systems = {}
systems["Ska"] = io.read(os.path.join("map","Ska.json"))

def get_tile(system_name,x,y):
	system = systems[system_name]
	x = str(x)
	y = str(y)
	if x not in system or y not in system[x]:
		return {}
	else:
		return system[x][y]
