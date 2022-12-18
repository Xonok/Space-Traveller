from . import defs,map,structure,items,ship,error

def accept(self,data,pdata):
	pship = ship.get(pdata.ship())
	qid = data["quest-id"]
	px,py = pship.get_coords()
	tstructure = structure.get(pship.get_system(),px,py)
	if not tstructure: raise error.User("Quests can only be accepted while at a structure.")
	if qid not in defs.quests: raise error.User("There is no quest with id "+qid+".")
	if qid not in tstructure["quests"]: raise error.User("This structure doesn't offer that quest.")
	if qid in pdata["quests"]: raise error.User("You have already accepted this quest.")
	pdata["quests"][qid] = "active"
	pdata.save()
def cancel(self,data,pdata):
	qid = data["quest-id"]
	if qid not in pdata["quests"]: raise error.User("Can't cancel. You haven't accepted the quest "+qid)
	del pdata["quests"][qid]
	pdata.save()
def submit(self,data,pdata):
	pship = ship.get(pdata.ship())
	qid = data["quest-id"]
	px,py = pship.get_coords()
	tstructure = structure.get(pship.get_system(),px,py)
	if not tstructure: raise error.User("Quests can only be submitted while at a structure.")
	if qid not in pdata["quests"]: raise error.User("Can't submit. You haven't accepted the quest "+qid)
	if pdata["quests"][qid] != "active": raise error.User("Can't submit. Quest status is not \"active\"")
	quest = defs.quests[qid]
	if tstructure["name"] != quest["objectives"]["location"]: raise error.User("Can't submit quest "+qid+" at this place.")
	sitems = tstructure["inventory"]["items"]
	pitems = pship.get_items()
	ritems = quest["rewards"]["items"]
	oitems = quest["objectives"]["items"]
	items.transaction(sitems,pitems,ritems,oitems)
	pdata["quests"][qid] = "completed"
	pdata.save()
	pship.save()
