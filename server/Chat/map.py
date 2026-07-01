import time
from server import Map,ship,defs,archaeology
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
	cdata = defs.characters.get(server.cname)
	pship = ship.get(cdata["ship"])
	pos = pship["pos"]
	system = pos["system"]
	x = pos["x"]
	y = pos["y"]
	send_tile_ships(cdata["name"],system,x,y)
	get_struct_positions(client,server)
	get_landmark_positions(client,server)
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
def get_landmark_positions(client,server):
	system = server.system
	positions = Map.query.get_map_landmarks(system)
	positions_out = {}
	for x,col in positions.items():
		for y,ships in col.items():
			for sname in ships:
				entity = defs.landmarks.get(sname)
				positions_out[entity["name"]] = {
					"x": entity["pos"]["x"],
					"y": entity["pos"]["y"],
					"img": defs.landmark_types[entity["type"]]["img"]
				}
	api.send_to_client("receive-landmark-positions",client,landmark_positions=positions_out)
def remove_char(cname):
	cdata = defs.characters[cname]
	if cname in api.clients:
		ws = api.clients[cname]
		ws.server.system = ""
	snames = cdata["ships"]
	remove_ships(snames)
def add_char(cname,system,x,y):
	cdata = defs.characters[cname]
	snames = cdata["ships"]
	add_ships(snames)
	pship = ship.get(cdata["ship"])
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
	entity = defs.structures.get(sname)
	system = entity["pos"]["system"]
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
	Map.update_structure_pos(sname,pos["x"],pos["y"],system)
	api.send_to_system("add-structure",system,position=data)
def remove_landmark(ename):
	entity = defs.landmarks.get(ename)
	system = entity["pos"]["system"]
	api.send_to_system("remove-landmark",system,ename=ename)
	Map.remove_landmark(ename)
def add_landmark(ename):
	entity = defs.landmarks[ename]
	pos = entity["pos"]
	system = pos["system"]
	data = {
		"name": ename,
		"x": pos["x"],
		"y": pos["y"],
		"img": defs.landmark_types[entity["type"]]["img"]
	}
	Map.update_landmark_pos(ename,pos["x"],pos["y"],system)
	api.send_to_system("add-landmark",system,position=data)
#NOTE: these 2 functions should share the same representation of a ship.
#Tell about the ships on a specific tile.
def send_tile_ships(cname,system,x,y):
	#Figure out where the list of ships per tile is kept.
	#Annoyance: having to specify .query, even though get_ is already clear enough.
	#Idea: maybe variables should have types prefixed for clarity. Issue: basically a comment, so not checked.
	ship_names = Map.query.get_tile_ships(system,x,y)
	owners = []
	for sname in ship_names:
		#Annoyance: getting the owner of a ship(a relation) requires 2 steps.
		pship = defs.ships[sname]
		owner = pship["owner"]
		if owner not in owners and owner != cname:
			owners.append(owner)
	tile_ships = {}
	for sname in ship_names:
		pship = defs.ships[sname]
		table = {
			"id":pship["id"],
			"type":pship["type"],
			"name":pship["name"],
			"owner":pship["owner"],
			"player":pship["owner"] not in defs.npc_characters,
			"threat":pship["stats"]["threat"],
			"size":pship["stats"]["size"],
			#"stats":,
			"img":pship["img"]
		}
		if pship["owner"] == cname:
			table["stats"] = pship["stats"]
		tile_ships[pship["name"]] = table
	cdata = defs.characters[cname]
	tstructure = Map.query.get_tile_structure(cdata,system,x,y)
	if tstructure:
		tstructure["threat"] = 0
		#This is currently redundant, but I want it to not be.
		tstructure["excavate"] = archaeology.can_excavate(cdata,tstructure)
		tstructure["size"] = 0
		tile_ships[tstructure["name"]] = tstructure
	api.send_to_character("set-tile-ships",cname,tile_ships=tile_ships)
#Tell everyone on the tile about the ships that entered.
def share_entering_ships(x,y,snames):
	pass
api.register_command("get-ship-positions",get_ship_positions)
