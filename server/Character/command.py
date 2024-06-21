
slots_by_swarm_level = [0,1,3,6,10,15,21,28,36,45,55,66,78,91,105,120,136,153,171,190,210]
ships_by_command_level = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]

slots_by_command = [0,2,4,6,8,12]
slot_req = [1,2,4,6,8,12,16]
slot_req_swarm = [1,1,2,4,6,8,12]
def get_max_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	return slots_by_command[command_lvl]
def get_used_slots(cdata):
	command_lvl = cdata["skills"].get("command",0)
	swarm_lvl = cdata["skills"].get("command",0)
	#go through each ship
	#decide how many slots it requires
	#don't count the biggest ship