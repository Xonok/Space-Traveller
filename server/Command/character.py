from . import api
from server import defs,quest,structure,exploration,Item,ship,reputation,Skill

def do_get_quests(cdata):
	pass
def do_quest_accept(server,cdata,quest_id="str"):
	quest.accept(server,quest_id,cdata)
def do_quest_cancel(server,cdata,quest_id="str"):
	quest.cancel(server,quest_id,cdata)
def do_quest_submit(server,cdata,quest_id="str"):
	return {
		"quest_end_text": quest.submit(server,quest_id,cdata)
	}
def do_skill_train(cdata,pship,name="str"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	Skill.train_skill(cdata,name,tstructure)
def do_set_home(cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.set_home(cdata)
def do_get_profile(cdata):
	msg = {}
	msg["achievements"] = exploration.get_achievements(cdata)
	msg["net_worth"] = Item.query.net_worth(cdata)
	msg["pships"] = ship.character_ships(cdata["name"])
	msg["structures"] = structure.character_structures(cdata["name"])
	msg["reputation"] = reputation.get_total(cdata["name"])
	msg["skills"] = Skill.get_character_skills(cdata)
	return msg
api.register("get-quests",do_get_quests,"character-quests")
api.register("quest-accept",do_quest_accept,"local-quests","character-quests")
api.register("quest-cancel",do_quest_cancel,"local-quests","character-quests")
api.register("quest-submit",do_quest_submit,"local-quests","character-quests")
api.register("skill-train",do_skill_train)
api.register("set-home",do_set_home)
api.register("get-profile",do_get_profile)