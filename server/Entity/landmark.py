from server import defs,io,error,map

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
		if "props" not in self:
			self["props"] = {}
	def save(self):
		io.write2("landmarks",self["id"],self)
	def delete(self):
		del defs.landmarks[self["id"]]
		io.delete(self,"data","landmarks",self["id"]+".json")
def create(id,name,type,psystem,px,py):
	landmark = Landmark()
	landmark[id] = id
	landmark[name] = name
	landmark[type] = type
	defs.landmarks[id] = landmark
	otiles = map.otiles(psystem)
	otile = otiles.get(px,py)
	if "landmarks" not in otile:
		otile["landmarks"] = []
	otile["landmarks"].append(landmark)
	otiles.set(px,py,otile)
	otiles.save()
	return landmark
def init():
	for id,data in defs.landmark_types.items():
		if id not in defs.landmarks:
			defs.landmarks[id] = create(id,data["name"],data["type"])
def get(psystem,px,py):
	otile = defs.objmaps[psystem]["tiles"].get(px,py)
	if "landmark" in otile:
		return defs.landmarks[tile["landmark"]]