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
	data = {
		"event": "receive-ship-positions",
		"data": {
			"positions": positions_out
		}
	}
	client.send_msg(data)
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
	update_ship_pos(snames)
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
		Map.update_ship_pos(pship["owner"],sname,pos["x"],pos["y"],system)
		positions[sname] = {
			"x": pos["x"],
			"y": pos["y"],
			"rotation": pos["rotation"]
		}
	data = {
		"event": "update-ship-positions",
		"data": {
			"positions": positions,
			"start_time": now,
			"end_time": future
		}
	}
	for cname,ws in api.clients.items():
		if ws.server.system == system:
			ws.send_msg(data)
def remove_ships(snames):
	pship = ship.get(snames[0])
	system = pship["pos"]["system"]
	data = {
		"event": "remove-ships",
		"data": {
			"snames": snames
		}
	}
	for cname,ws in api.clients.items():
		if ws.server.system == system:
			ws.send_msg(data)
	Map.remove_ships(snames)
api.register_command("get-ship-positions",get_ship_positions)
