import time
from server import defs,io,error,map,tick

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

class Landmark(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def save(self):
		io.write2("landmarks",self["id"],self)
	def delete(self):
		del defs.landmarks[self["id"]]
		io.delete(self,"data","landmarks",self["id"]+".json")
def create(id,name,type,psystem,px,py):
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
	defs.landmarks[id] = landmark
	otiles = map.otiles(psystem)
	otile = otiles.get(px,py)
	otile["landmark"] = id
	otiles.set(px,py,otile)
	otiles.save()
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
					create(id,landmark["name"],landmark["type"],system,x,y)
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
