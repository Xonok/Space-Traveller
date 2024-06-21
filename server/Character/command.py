from server import ship,defs

slots_by_swarm_level = [0,1,3,6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,190,210]
ships_by_command_level = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]

slots_by_command = [0,2,4,6,8,12]
slot_req = [2,4,6,8,12,16]
slot_req_swarm = [2,4,6,8,12,16]
def update_command_slots(cdata):
	update_max_slots(cdata)
	update_used_slots(cdata)
def update_max_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	cdata["command_max"] = slots_by_command[command_lvl]
def update_used_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	swarm_lvl = cdata["skills"].get("swarm",0) #not in use yet
	pships = ship.character_ships(cdata["name"])
	slots_used = 0
	max_slots = 0
	for name,pship in pships.items():
		ship_def = defs.ship_types[pship["type"]]
		tech = ship_def["tech"]
		ship_slots = slot_req[tech]
		slots_used += ship_slots
		max_slots = max(ship_slots,max_slots)
		print(pship["type"],ship_slots)
	print("max",max_slots)
	cdata["command_used"] = slots_used-max_slots