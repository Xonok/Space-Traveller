import time
from server import Map,ship,defs
from . import api

def update_active_char(client,server):
	del api.clients[server.cname]
	udata = defs.users.get(server.uname)
	server.cname = udata["active_character"]
	server.system = defs.characters[server.cname].get_system()
	api.clients[server.cname] = client
def get_ship_positions(client,server):
	update_active_char(client,server)
	system = server.system
	positions = Map.query.get_map_ships(system)
	positions_out = {}
	for x,col in positions.items():
		for y,ships in col.items():
			for sname in ships:
				pship = ship.get(sname)
				positions_out[pship["name"]] = {
					"x": pship["pos"]["x"],
					"y": pship["pos"]["y"],
					"rotation": pship["pos"]["rotation"],
					"type": pship["type"]
				}
	api.send_to_client("receive-ship-positions",client,positions=positions_out)
	get_struct_positions(client,server)
def get_struct_positions(client,server):
	system = server.system
	positions = Map.query.get_map_structs(system)
	positions_out = {}
	for x,col in positions.items():
		for y,ships in col.items():
			for sname in ships:
				tstruct = defs.structures.get(sname)
				positions_out[tstruct["name"]] = {
					"x": tstruct["pos"]["x"],
					"y": tstruct["pos"]["y"],
					"type": tstruct["ship"],
					"subtype": tstruct["type"]
				}
	api.send_to_client("receive-structure-positions",client,struct_positions=positions_out)
def remove_char(cname):
	cdata = defs.characters[cname]
	if cname in api.clients:
		ws = api.clients[cname]
		ws.server.system = ""
	snames = cdata["ships"]
	remove_ships(snames)
def add_char(cname):
	cdata = defs.characters[cname]
	snames = cdata["ships"]
	add_ships(snames)
	pship = ship.get(cdata["ship"])
	system = pship["pos"]["system"]
	if cname in api.clients:
		ws = api.clients[cname]
		ws.server.system = system
		get_ship_positions(ws,ws.server)
def char_update_pos(cname,psystem):
	if cname in api.clients:
		ws = api.clients[cname]
		ws.server.system = psystem
		get_ship_positions(ws,ws.server)
def update_ship_pos(snames,future=None):
	system = None
	positions = {}
	now = time.time()
	if future is None:
		future = now
	for sname in snames:
		pship = ship.get(sname)
		pos = pship["pos"]
		system = pos["system"]
		Map.update_ship_pos(sname,pos["x"],pos["y"],system)
		positions[sname] = {
			"x": pos["x"],
			"y": pos["y"],
			"rotation": pos["rotation"]
		}
	api.send_to_system("update-ship-positions",system,positions=positions,start_time=now,end_time=future)
def remove_ships(snames):
	pship = ship.get(snames[0])
	system = pship["pos"]["system"]
	api.send_to_system("remove-ships",system,snames=snames)
	Map.remove_ships(snames)
def add_ships(snames):
	system = None
	positions = {}
	for sname in snames:
		pship = ship.get(sname)
		pos = pship["pos"]
		system = pos["system"]
		Map.update_ship_pos(sname,pos["x"],pos["y"],system)
		positions[sname] = {
			"x": pos["x"],
			"y": pos["y"],
			"rotation": pos["rotation"],
			"type": pship["type"]
		}
	api.send_to_system("add-ships",system,positions=positions)
def remove_structure(sname):
	pship = ship.get(snames[0])
	system = pship["pos"]["system"]
	api.send_to_system("remove-structure",system,sname=sname)
	Map.remove_structure(sname)
def add_structure(sname):
	entity = defs.structures[sname]
	pos = entity["pos"]
	system = pos["system"]
	data = {
		"name": sname,
		"x": pos["x"],
		"y": pos["y"],
		"type": entity["ship"]
	}
	Map.update_struct_pos(sname,pos["x"],pos["y"],system)
	api.send_to_system("add-structure",system,position=data)
api.register_command("get-ship-positions",get_ship_positions)
