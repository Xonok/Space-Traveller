import math
from . import defs,error,items
def start(data,user,tstructure):
	if tstructure["owner"] != user["name"]:	raise error.User("You don't own this station.")
	blueprint_name = data["blueprint"]
	if "blueprints" not in tstructure or blueprint_name not in tstructure["blueprints"]:
		raise error.User("The station doesn't have this blueprint equipped.")
	blueprint = defs.blueprints[blueprint_name]
	sitems = tstructure["inventory"]["items"]
	for item,amount in blueprint["inputs"].items():
		if not sitems.get(item) >= amount: raise error.User("Need "+str(amount)+" "+item+" to start building "+blueprint_name)
	for item,amount in blueprint["inputs"].items():
		sitems.add(item,-amount)
	if "builds" not in tstructure:
		tstructure["builds"] = []
	progress = {
		"active": True,
		"blueprint": blueprint_name,
		"labor": 0,
		"labor_needed": blueprint["labor"]
	}
	tstructure["builds"].append(progress)
	tstructure.get_room()
	tstructure.save()
def update(user):
	if "industries" not in user: return
	cdata = defs.characters[user["owner"]]
	construction = None
	for data in user["industries"]:
		if data["name"] == "construction":
			construction = data
	if not construction: return
	sitems = user.get_items()
	workers = construction["workers"]
	max_robots = 0
	for item,amount in user["inventory"]["gear"].items():
		idata = defs.items[item]
		props = idata.get("props",{})
		max_robots += props.get("robots_max_construction",0)*amount
	if "robots" in sitems:
		workers += min(sitems["robots"],max_robots)
	builds = user["builds"] if "builds" in user else []
	for build in list(builds):
		blueprint = defs.blueprints[build["blueprint"]]
		remaining_work = build["labor_needed"]-build["labor"]
		max_workers = blueprint["max_workers"] if "max_workers" in blueprint else 999999999
		actual_work = min(workers,remaining_work,max_workers)
		build["labor"] += actual_work
		workers -= actual_work
		if build["labor"] == build["labor_needed"]:
			room_required = 0
			tech = 0
			for item,amount in blueprint["outputs"].items():
				idata = defs.items[item]
				tech = max(tech,idata.get("tech",0))
				room_required += items.size(item)*amount
			if user.get_room() >= room_required:
				for item,amount in blueprint["outputs"].items():
					user["inventory"]["items"].add(item,amount)
				user.get_room()
				builds.remove(build)
				if build["labor_needed"]/1000 > 1:
					build_level = math.log(build["labor_needed"]/1000,2)*(1+tech/2)
					self_level = cdata["level"]
					if self_level < build_level:
						mod = 2 if self_level < 10 else 5
					else:
						mod = 0.9
					xp = min(1000,int(200*((build_level+1)/(self_level+1))**mod))
					new_xp = cdata["xp"] + xp
					prev_level = cdata["level"]
					while new_xp >= 1000:
						new_xp -= 1000
						cdata["level"] += 1
					cdata["xp"] = new_xp
					print("Construction done.",build_level,self_level,mod,xp)
	user.save()
def equip_blueprint(data,user,tstructure,pship):
	if tstructure["owner"] != user["name"]:	raise error.User("You don't own this station.")
	blueprint_name = data["blueprint"]
	pinv = pship["inventory"]["items"]
	if blueprint_name not in pinv: raise error.User("Don't have this item.")
	if "blueprints" not in tstructure:
		tstructure["blueprints"] = []
	if blueprint_name in tstructure["blueprints"]: raise error.User("The station already has this blueprint.")
	tstructure["blueprints"].append(blueprint_name)
	pinv.add(blueprint_name,-1)
	tstructure.save()
	pship.save()
def get_bp_info(tstructure):
	info = {}
	if "blueprints" not in tstructure: return info
	for bp in tstructure["blueprints"]:
		info[bp] = defs.blueprints[bp]
	return info