import copy,time
from . import defs,ship,structure,error

def get_data(name):
	return defs.quests.get(name)
def accepted(cdata,name):
	qdata = get_data(name)
	return qdata["name"] in cdata["quests"]
def completed(cdata,name):
	qdata = get_data(name)
	if "quests_completed" not in cdata:
		cdata["quests_completed"] = {}
	return qdata["name"] in cdata["quests_completed"]
def potential(cdata,name):
	qdata = get_data(name)
	potential = True
	if "quests_completed" not in cdata:
		cdata["quests_completed"] = {}
		cdata.save()
	if "completed_quests" in qdata["potential"]:
		for q in qdata["potential"]["completed_quests"]:
			if q not in cdata["quests_completed"]:
				potential = False
				break
	return potential
def visible(cdata,name):
	return accepted(cdata,name) or potential(cdata,name)
def local(cdata,name):
	pship = ship.get(cdata.ship())
	tstructure = structure.from_pos(pship["pos"])
	names = tstructure.get("quests",[])
	return name in names
def objectives(cdata,qdata):
	array = []
	entry = cdata["quests"].get(qdata["name"])
	outcome = qdata["outcomes"][0]
	objs = outcome["objectives"]
	if "location" in objs:
		table = {}
		table["completed"] = False
		table["desc"] = "Be at "+objs["location"]
		table["status"] = "no"
		table["props"] = {}
		array.append(table)
	cdata.save()
	return array
def get_sanitized(name,cdata):
	qdata = copy.deepcopy(get_data(name))
	qdata["outcome"] = qdata["outcomes"][0]
	qdata["objectives"] = objectives(cdata,qdata)
	del qdata["outcomes"]
	del qdata["potential"]
	return qdata
def get_local(cdata):
	pship = ship.get(cdata.ship())
	tstructure = structure.from_pos(pship["pos"])
	names = tstructure.get("quests",[])
	data = {}
	for name in names:
		if visible(cdata,name):
			qdata = get_sanitized(name,cdata)
			data[qdata["name"]] = qdata
	return data
def get_character(cdata):
	entries = cdata["quests"]
	table = {}
	for name,entry in entries.items():
		qdata = get_sanitized(name,cdata)
		table[name] = qdata
		#print(name,entry,qdata)
	return table
def accept(self,data,cdata):
	name = data["quest-id"]
	if accepted(cdata,name): raise error.User("You have already accepted that quest.")
	if completed(cdata,name): raise error.User("You've already completed this quest.")
	if not visible(cdata,name) or not potential(cdata,name): raise error.User("The quest isn't available: "+name)
	entry = {
		"started": time.time(),
		"props": {}
	}
	cdata["quests"][name] = entry
	cdata.save()
	print(name)
def cancel(self,data,cdata):
	name = data["quest-id"]
	if not accepted(cdata,name): raise error.User("You don't have that quest.")
	del cdata["quests"][name]
	cdata.save()