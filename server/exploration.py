import time,copy
from server import defs,types,Skill,io

class Achievements(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def save(self):
		io.write2("achievements",self["name"],self)
def default_params(name):
	return {
		"name": name,
		"discovered": {},
		"visited": {},
		"killed": {}
	}
def check_character(cdata):
	name = cdata["name"]
	if name in defs.npc_characters: return
	if name not in defs.achievements:
		defs.achievements[name] = types.make(default_params(name),"achievements")
def check_discover(cdata,system_name,self):
	pass
def check_visit(cdata,struct_name,self):
	if struct_name not in defs.predefined_structures: return
	predef = defs.predefined_structures[struct_name]
	level = predef["level"]
	check_character(cdata)
	achievements = defs.achievements[cdata["name"]]
	visited = achievements["visited"]
	if struct_name not in visited:
		visited[struct_name] = {
			"time": time.time()
		}
		xp_amount = (10+level-cdata["level"])*10
		if xp_amount > 0:
			Skill.gain_xp_flat(cdata,xp_amount)
			if self:
				self.add_message("Visited "+struct_name+" for the first time. Gained "+str(xp_amount)+"xp, "+str(1000-cdata["xp"])+" until next level.")
		else:
			if self:
				self.add_message("Visited "+struct_name+" for the first time.")
	achievements.save()
def register_kill(cdata,pship):
	predef = pship.get("predef")
	if not predef: return
	if cdata["name"] in defs.npc_characters: return
	if pship["owner"] not in defs.npc_characters: return
	achievements = defs.achievements[cdata["name"]]
	killed = achievements["killed"]
	if predef not in killed:
		killed[predef] = {
			"time_first": time.time(),
			"time_last": None,
			"amount": 0
		}
	killed[predef]["amount"] += 1
	killed[predef]["time_last"] = time.time()
	achievements.save()
def get_achievements(cdata):
	ach = copy.deepcopy(defs.achievements[cdata["name"]])
	for key,data in ach["killed"].items():
		data["name"] = defs.premade_ships[key]["default_name"]
		data["img"] = defs.ship_types[defs.premade_ships[key]["ship"]]["img"]
	return ach