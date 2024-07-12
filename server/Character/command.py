from server import ship,defs,stats

slots_by_swarm_level = [0,1,3,6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,190,210]
ships_by_command_level = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]

slots_by_command = [0,2,4,6,8,12]
slot_req = [2,4,6,8,12,16]
slot_req_swarm = [2,4,6,8,12,16]
def update_command_slots(cdata):
	update_max_slots(cdata)
	update_used_slots(cdata)
	update_ships(cdata)
	cdata.save()
def update_max_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	cdata["command_max"] = slots_by_command[command_lvl]
def update_used_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	swarm_lvl = cdata["skills"].get("swarm",0) #not in use yet
	pships = ship.active_ships(cdata)
	slots_used_freight = 0
	max_slots_freight = 0
	slots_used_battle = 0
	max_slots_battle = 0
	for name,pship in pships.items():
		ship_def = defs.ship_types[pship["type"]]
		tech = ship_def["tech"]
		freight = ship_def.get("freight",0)
		slots_used_freight += freight
		max_slots_freight = max(freight,max_slots_freight)
	for name,pship in pships.items():
		if not valid_fighter(pship): continue
		ship_def = defs.ship_types[pship["type"]]
		tech = ship_def["tech"]
		battle = ship_def.get("battle",0)
		slots_used_battle += battle
		max_slots_battle = max(battle,max_slots_battle)
	cdata["command_battle_used"] = slots_used_battle-max_slots_battle
	cdata["command_freight_used"] = slots_used_freight-max_slots_freight
def valid_fighter(pship):
	has_weapons = False
	for item in pship["inventory"]["gear"].keys():
		if item in defs.weapons:
			has_weapons = True
	return pship["stats"]["hull"]["current"] > 1 and has_weapons
def update_ships(cdata):
	for name in cdata["ships"]:
		pship = ship.get(name)
		stats.update_ship(pship)