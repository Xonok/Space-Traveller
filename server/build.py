from . import defs,error
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
	tstructure.save()
def update(user):
	workers = user["population"]["workers"]
	builds = user["builds"] if "builds" in user else []
	for build in list(builds):
		blueprint = defs.blueprints[build["blueprint"]]
		remaining_work = build["labor_needed"]-build["labor"]
		max_workers = blueprint["max_workers"] if "max_workers" in blueprint else 999999999
		actual_work = min(workers,remaining_work,max_workers)
		build["labor"] += actual_work
		workers -= actual_work
		if build["labor"] == build["labor_needed"]:
			space_required = 0
			for item,amount in blueprint["outputs"].items():
				space_required += items.size(item)*amount
			if user.get_space() >= space_required:
				for item,amount in blueprint["outputs"].items():
					user["inventory"]["items"].add(item,amount)
				user.get_space()
				builds.remove(build)
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
		info[bp] = defs.blueprints[bp.replace("bp_","")]
	return info