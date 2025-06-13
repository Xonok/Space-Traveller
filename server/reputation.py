
import math
from server import defs,func,Item

#Add rep by type
#Get XP from adding rep.
#Reduce rep by ticking it down. (fluid rep only)
#Handle trade
#Handle donations
#Handle quests
#Calculate rep amount from items

rep_per_quest = 1000
def handle_quest(cname,qdata):
	start_struct_id = qdata["start_location"]
	tstruct = defs.structures[start_struct_id]
	add_rep_by_type(tstruct,cname,"quest",rep_per_quest)
	tstruct.save()
	#run this on quest completion.
def handle_trade(cdata,tstruct,item,amount):
	if tstruct["name"] not in defs.predefined_structures: return 0
	cname = cdata["name"]
	balance = tstruct["market"]["balance"]
	itype = Item.query.type(item)
	commodity = itype == "common" or itype == "produced" or itype == "rare"
	no_xp = False
	effect = 0
	if item in balance["produced"] and item in balance["consumed"]:
		effect = 0
	elif item in balance["produced"]:
		effect = -1
	elif item in balance["consumed"]:
		effect = 1
	elif commodity:
		no_xp = True
		effect = -0.5
	
	rep = amount*effect*0.95
	rep_static = amount*effect*0.05
	
	if rep < 0:
		rep *= 3
		rep_static *= 3
	
	add_rep_by_type(tstruct,cname,"trade",rep)
	add_rep_by_type(tstruct,cname,"trade_static",rep_static)
	tstruct.save()
	
	if rep < 0 or no_xp:
		xp = 0
	else:
		cur_rep = get_rep_by_type(tstruct,cname,"trade")
		cur_rep += get_rep_by_type(tstruct,cname,"trade_static")
		cur_rep += get_rep_by_type(tstruct,cname,"quest")
		xp = rep_xp(cdata,cur_rep,rep)
	return xp
def get_rep_by_type(tstruct,cname,type):
	return func.table_get(tstruct,0.0,"props","rep",cname,type)
def add_rep_by_type(tstruct,cname,type,amount):
	func.table_add(tstruct,amount,0.0,"props","rep",cname,type)
def rep_xp(cdata,cur_rep,rep_amount):
	name = cdata["name"]
	mult = 1 #TODO: should depend on location
	noob_factor = 1
	if cdata["level"] < 10:
		noob_factor += (9-cdata["level"])/2
	rep_factor = 1
	if cur_rep > 0:
		rep_factor = 1+math.log(max(cur_rep/100,1),2)/5
	elif cur_rep < 0:
		rep_factor = 1/(1+math.log(max(-cur_rep/100,1),2)/5)
	level_factor = 1/(cdata["level"]+1)
	xp = func.f2ir(abs(rep_amount)*level_factor*mult*noob_factor*rep_factor)
	return xp
def tick(tstruct):
	if tstruct["name"] not in defs.predefined_structures: return
	props = tstruct.get("props",{})
	rep = props.get("rep",{})
	to_delete = []
	for cname,data in rep.items():
		old_rep = func.table_get(tstruct,0,"props","reputation",cname)
		trade_rep = get_rep_by_type(tstruct,cname,"trade") + old_rep*0.95
		if old_rep:
			data["trade_static"] = old_rep*0.05
		if trade_rep > 0:
			data["trade"] = trade_rep*0.995-1
		else:
			data["trade"] = trade_rep*0.995+1
		total = 0
		for name,val in data.items():
			total += val
		if total > -1 and total < 1:
			to_delete.append(cname)
	for cname in to_delete:
		del rep[cname]
	if "reputation" in props:
		del props["reputation"]
def init():
	#reset previous quest rep
	for name in defs.predefined_structures.keys():
		tstruct = defs.structures[name]
		reps = func.table_get(tstruct,{},"props","rep")
		for cname,data in reps.items():
			data["quest"] = 0
	#recalculate
	for cname,cdata in defs.characters.items():
		q_done = cdata.get("quests_completed",{}).keys()
		for q_id in q_done:
			qdata = defs.quests[q_id]
			handle_quest(cname,qdata)
	#calculate rep from quests
def get_total(cname):
	result = 0
	for struct_name in defs.predefined_structures.keys():
		tstruct = defs.structures.get(struct_name)
		result += get_rep_by_type(tstruct,cname,"trade")
		result += get_rep_by_type(tstruct,cname,"trade_static")
		result += get_rep_by_type(tstruct,cname,"quest")
	return result
