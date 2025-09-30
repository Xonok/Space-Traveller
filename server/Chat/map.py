from server import Map,ship
from . import api

def get_ship_positions(client,server):
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
def update_ship_pos(system,positions):
	data = {
		"event": "update-ship-positions",
		"data": {
			"positions": positions
		}
	}
	for cname,ws in api.clients.items():
		if ws.server.system == system:
			ws.send_msg(data)
api.register_command("get-ship-positions",get_ship_positions)

