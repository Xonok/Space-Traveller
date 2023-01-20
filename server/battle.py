from . import ship,error,map,player
battles = []
ship_battle = {}
def get(pship):
	if pship["name"] in ship_battle:
		return ship_battle[pship["name"]]
def start_battle(data,pdata):
	new_battle = {
		"attackers": [],
		"defenders": [],
		"logs": []
	}
	pships = ship.gets(pdata["name"])
	for pship in pships.values():
		new_battle["attackers"].append(pship["name"])
		ship_battle[pship["name"]] = new_battle
	target = ship.get(data["target"])
	defenders = map.get_player_ships(player.data(target["owner"]))
	for d_ship in defenders.values():
		new_battle["defenders"].append(d_ship["name"])
		ship_battle[d_ship["name"]] = new_battle
	battles.append(new_battle)
	raise error.Battle()