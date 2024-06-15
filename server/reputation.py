
def check_structure(tstruct):
	if "props" not in tstruct:
		tstruct["props"] = {}
	if "reputation" not in tstruct["props"]:
		tstruct["props"]["reputation"] = {}
def add_rep(cdata,tstruct,item,amount):
	check_structure(tstruct)
	rep = tstruct["props"]["reputation"]
	name = cdata["name"]
	balance = tstruct["market"]["balance"]
	if item in balance["produced"] and item in balance["consumed"]:
		effect = 0
	elif item in balance["produced"]:
		effect = -1
	elif item in balance["consumed"]:
		effect = 1
	else:
		return
	rep_amount = int(amount*effect)
	if rep_amount < 0:
		rep_amount = int(rep_amount*3)
	print(tstruct)
	print(item,amount)
	if name not in rep:
		rep[name] = 0
	rep[name] += rep_amount
	tstruct.save()
def tick(tstruct):
	#decay all reputation counters, remove those that are at 0.
	check_structure(tstruct)
	rep = tstruct["props"]["reputation"]
	to_delete = []
	for name,amount in rep.items():
		if amount > 0:
			rep[name] = round(amount*0.995-1)
		else:
			rep[name] = round(amount*0.995+1)
		if rep[name] == 0:
			to_delete.append(name)
	for name in to_delete:
		del rep[name]
		