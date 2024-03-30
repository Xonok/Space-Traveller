from . import defs

def calculate(pship):
	expected_hits = 3
	expected_rounds = 4
	total_defense = 0
	total_offense = 0
	pstats = pship["stats"]
	total_defense += pstats["hull"]["max"]
	total_defense += pstats["armor"]["max"]
	total_defense += pstats["shield"]["max"]
	total_defense += pstats["shield"]["reg"]*expected_rounds
	for item,amount in pship["inventory"]["gear"].items():
		if item in defs.weapons:
			wdef = defs.weapons[item]
			charge = wdef.get("charge",1)
			aoe = wdef.get("targets",0)/2 #extra targets count for half
			if wdef.get("preload"):
				charge = ((charge-1)/2)+1
			burst = (wdef["damage"]*wdef["shots"])*(1+aoe)
			dpr = (wdef["damage"]*wdef["shots"])*(1+aoe)/charge
			if wdef["type"] == "missile":
				dpr /= 2
			if wdef["type"] == "drone":
				dpr /= 2
			total_offense += burst+dpr
	result = int((total_defense*total_offense)**0.5)
	#print(pship["name"],total_defense,total_offense,result)
	return result
