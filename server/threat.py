from . import defs,Skill

ship_types = []
def calculate(pship):
	cdata = defs.characters[pship["owner"]]
	expected_hits = 3
	expected_rounds = 4
	total_defense = 0
	total_offense = 0
	pstats = pship["stats"]
	ship_type = defs.ship_types[pship.get("ship",pship["type"])]
	total_defense += pstats["hull"]["max"]
	total_defense += pstats["armor"]["max"]
	total_defense += pstats["shield"]["max"]
	total_defense += pstats["shield"]["reg"]*expected_rounds
	agility = pstats["agility"]
	tracking = pstats["tracking"]
	for item,amount in pship["inventory"]["gear"].items():
		if item in defs.weapons:
			skill_factor = Skill.query.skill_factor(cdata,item)
			wdef = defs.weapons[item]
			dam = wdef.get("damage")
			dam_shield = wdef.get("damage_shield",0)
			dam_armor = wdef.get("damage_armor",0)
			dam_hull = wdef.get("damage_hull",0)
			dam += (dam_shield+dam_armor+dam_hull)/2
			dam *= skill_factor
			charge = wdef.get("charge",1)
			aoe = wdef.get("targets",0)/2 #extra targets count for half
			if wdef.get("preload"):
				charge = ((charge-1)/2)+1
			burst = (dam*wdef["shots"])*(1+aoe)*amount
			dpr = (dam*wdef["shots"])*(1+aoe)*amount/charge
			if wdef["type"] == "missile":
				dpr /= 2
			if wdef["type"] == "drone":
				dpr /= 2
			offense = burst+dpr
			if wdef["type"] == "laser":
				offense *= 1.5
			if wdef["type"] != "missile" and wdef["type"] != "drone":
				offense *= (agility+tracking)/100
			total_offense += offense
	total_defense *= 1.+(agility/100)
	result = int((total_defense*total_offense)**0.5)
	#if ship_type["name"] not in ship_types:
		#print(pship["name"],total_defense,total_offense,result)
		#ship_types.append(ship_type["name"])
	return result
