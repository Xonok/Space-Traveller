from . import defs,map,structure

def accept(self,data,pdata):
	qid = data["quest-id"]
	px,py = pdata.get_coords()
	stiles = map.get_system(pdata.get_system())["tiles"]
	tstructure = structure.get(stiles,px,py)
	if qid not in defs.quests: return
	if not tstructure: return
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
	#is accepted
	#can finish
	pass
