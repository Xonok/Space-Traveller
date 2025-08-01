import time,_thread,random,time
from server import defs,io,error,map,tick,Tick

#There are 3 kinds of landmarks.
#1. Planets with the potential for colonies.
#2. Static landmarks, such as obelisks.
#3. Generated landmarks, such as comets or wrecks.
#
#Planets and static landmarks are essentially very similar and rather easy to support.
#Generated landmarks could possibly be recycled.
#Perhaps if they're using numbered IDs they can simply be wiped when recycling?
#
#Perhaps the generated ones could be extended with mining, anomalies, w/e.
#For now let's focus on the most simple cases of 1. and 2.

#Keep track of landmarks that aren't static.
landmarks = {}

class Landmark(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def save(self):
		io.write2("landmarks",self["id"],self)
	def delete(self):
		del defs.landmarks[self["id"]]
		io.delete(self,"data","landmarks",self["id"]+".json")
def create(id,name,type,psystem="",px=0,py=0):
	landmark = Landmark()
	landmark["id"] = id
	landmark["name"] = name
	landmark["type"] = type
	landmark["pos"] = {
		"x": int(px),
		"y": int(py),
		"system": psystem,
		"rotation": 0
	}
	landmark["props"] = {}
	landmark.save()
	return landmark
def init():
	for system,sysdata in defs.systems.items():
		for x,col in sysdata["tiles"].items():
			for y,tile in col.items():
				otiles = defs.objmaps[system]["tiles"]
				otile = otiles.get(x,y)
				landmark = tile.get("landmark")
				if landmark and "landmark" not in otile:
					id = system+","+landmark["type"]+","+str(x)+","+str(y)
					lm = create(id,landmark["name"],landmark["type"],system,x,y)
					defs.landmarks[id] = lm
					otiles = map.otiles(system)
					otile = otiles.get(x,y)
					otile["landmark"] = id
					otiles.set(x,y,otile)
					otiles.save()
	for landmark_type,data in defs.landmark_types.items():
		if "spawner" not in data: continue
		spawner = data["spawner"]
		limit = spawner["limit"]
		for i in range(limit):
			id = landmark_type+","+str(i)
			if id in defs.landmarks:
				landmarks[id] = defs.landmarks[id]
			else:
				landmarks[id] = create(id,data["name"],landmark_type)
def get(psystem,px,py):
	otile = defs.objmaps[psystem]["tiles"].get(px,py)
	if "landmark" in otile:
		return defs.landmarks[otile["landmark"]]
def get2(id):
	return defs.landmarks.get(id)
def update(psystem,px,py):
	lm = get(psystem,px,py)
	if not lm: return
	props = lm["props"]
	lm_def = defs.landmark_types[lm["type"]]
	now = time.time()
	if "timestamp" not in props:
		props["timestamp"] = now
	timestamp = props["timestamp"]
	def_res = lm_def.get("resources")
	ticks = tick.ticks_since(timestamp,"long")
	ticks = max(ticks,0)
	if def_res:
		if "resources" not in props:
			props["resources"] = {}
		res = props.get("resources")
		for name,data in def_res.items():
			res_max = data.get("max")
			reg = data.get("reg")
			cur = res.get(name,res_max)
			cur += reg*ticks
			cur = min(cur,res_max)
			res[name] = cur
	props["timestamp"] = now
	lm.save()
def mine(target,resource,cdata,pship,server):
	lm = get2(target)
	if not lm:
		raise error.User("There is no landmark with the ID: "+target)
	if not map.pos_equal(lm["pos"],pship["pos"]):
		raise error.User("The landmark you're trying to mine is not here.")
	idata = defs.items.get(resource)
	if not idata:
		raise error.User("There is no item with the ID: "+resource)
	resources = lm["props"].get("resources")
	if resource not in resources:
		raise error.User("Can't mine "+resource+" on this landmark.")
	res_amount = resources[resource]
	if res_amount == 0:
		raise error.User("Can't mine this resource, since it's already depleted.")
	if cdata.get_room() < 1:
		raise error.User("You have no room left.")
	tech = idata.get("tech",0)
	skills = cdata.get("skills",{})
	mining_skill = skills.get("mining",0)
	if tech > mining_skill:
		raise error.User("You need mining skill "+str(mining_skill)+" to mine this resource.")
	cdata.get_items().add(resource,1)
	resources[resource] -= 1
	lm.save()
	cdata.save()
	server.add_message("Mined 1 "+idata["name"]+".")
def loop():
	#Figure out when the next spawn is and write it down.
	#Once spawn time is here, look for a valid tile.
	for id,data in landmarks.items():
		lm_def = defs.landmark_types[data["type"]]
		spawner = lm_def["spawner"]
		props = data["props"]
		now = time.time()
		if "next_spawn" not in props:
			#days
			props["next_spawn"] = now+random.randint(spawner["min_time"],spawner["max_time"])*86400
			print(id,"no spawn set")
			data.save()
			continue
		next = props["next_spawn"]
		if next < now:
			print(id,"spawning")
			#do spawn
			location = random.choice(spawner["locations"])
			constellation = location["constellation"]
			if constellation not in defs.constellations:
				raise Exception("Unknown constellation: "+constellation)
			stars = defs.constellations[constellation]
			star_name = random.choice(stars)
			star_data = defs.system_data[star_name]
			otiles = map.otiles(star_name)
			tile_found = False
			for i in range(5):
				tile = random.choice(star_data["tiles"])
				otile = otiles.get(tile["x"],tile["y"])
				if "landmark" not in otile:
					tile_found = True
					x = tile["x"]
					y = tile["y"]
					break
			if not tile_found: continue
			print(id,"spawned",star_name,",",x,",",y,int(x)==x)
			prev_otiles = map.otiles(data["pos"]["system"])
			prev_otile = prev_otiles.get(data["pos"]["x"],data["pos"]["y"])
			if "landmark" in prev_otile and prev_otile["landmark"] == id:
				del prev_otile["landmark"]
				prev_otiles.set(data["pos"]["x"],data["pos"]["y"],prev_otile)
				prev_otiles.save()
			props["next_spawn"] += random.randint(spawner["min_time"],spawner["max_time"])*86400
			data["pos"]["system"] = star_name
			data["pos"]["x"] = int(x)
			data["pos"]["y"] = int(y)
			otile["landmark"] = id
			otiles.set(x,y,otile)
			otiles.save()
			data.save()
			#get random system in constellation
			#get random tile in system(optionally limit by tile type)
			#(tiles with landmarks already on them aren't valid)
_thread.start_new_thread(Tick.schedule_periodic,(5,loop))