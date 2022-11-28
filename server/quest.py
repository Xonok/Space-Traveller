from . import defs,map,structure,items

def accept(self,data,pdata):
	qid = data["quest-id"]
	px,py = pdata.get_coords()
	stiles = map.get_system(pdata.get_system())["tiles"]
	tstructure = structure.get(stiles,px,py)
	if not tstructure: return
	if qid not in defs.quests: return
	if qid not in tstructure["quests"]: return
	if qid in pdata["quests"]: return
	pdata["quests"][qid] = "active"
	pdata.save()
def cancel(self,data,pdata):
	qid = data["quest-id"]
	if qid not in pdata["quests"]: return
	del pdata["quests"][qid]
	pdata.save()
def submit(self,data,pdata):
	qid = data["quest-id"]
	px,py = pdata.get_coords()
	stiles = map.get_system(pdata.get_system())["tiles"]
	tstructure = structure.get(stiles,px,py)
	if not tstructure: return
	if qid not in pdata["quests"]: return
	if pdata["quests"][qid] != "active": return
	quest = defs.quests[qid]
	if tstructure["name"] != quest["objectives"]["location"]: return
	sitems = tstructure["inventory"]["items"]
	pitems = pdata["inventory"]["items"]
	ritems = quest["rewards"]["items"]
	oitems = quest["objectives"]["items"]
	if not items.transaction(sitems,pitems,ritems,oitems): return
	pdata["quests"][qid] = "completed"
	pdata.save()
