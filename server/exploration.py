import time
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