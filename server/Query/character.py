from . import api
from server import Content,Entity,Skill,defs

def get_vision(cdata):
	return cdata.get_vision()
def get_local_quests(cdata):
	return Content.quest.get_local(cdata)
def get_character_quests(cdata):
	return Content.quest.get_character(cdata)
def get_skill_location(pship):
	psystem,px,py = pship.loc()
	tstructure = Entity.structure.get(psystem,px,py)
	if not tstructure: return
	return Skill.get_location(tstructure["name"])
def get_skill_data(pship):
	psystem,px,py = pship.loc()
	tstructure = Entity.structure.get(psystem,px,py)
	if not tstructure: return
	skill_loc = Skill.get_location(tstructure["name"])
	if not skill_loc:
		return {}
	return Skill.get_skill_data(skill_loc)

api.register_query("vision",get_vision)
api.register_query("local-quests",get_local_quests)
api.register_query("character-quests",get_character_quests)
api.register_query("skill-location",get_skill_location)
api.register_query("skill-data",get_skill_data)
