class Character(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
	def ship(self):
		if self["ship"] not in self["ships"]:
			self["ship"] = ""
		if self["ship"]: return self["ship"]
		self["ship"] = self["ships"][0]
		return self["ships"][0]
	def save(self):
		io.write2("characters",self["name"],self)

from . import io,defs,error

def data(name):
	if not name in defs.characters:
		raise Exception("No character called "+name+".")
	return defs.characters[name]
def remove_ship(pship):
	cdata = data(pship["owner"])
	name = pship["name"]
	if name in cdata["ships"]:
		cdata["ships"].remove(name)
	if cdata["ship"] == name:
		cdata["ship"] = ""
		if len(cdata["ships"]):
			cdata["ship"] = cdata["ships"][0]
def give_credits(cdata,data):
	target = data["target"]
	amount = data["amount"]
	tdata = defs.characters.get(target)
	if not tdata: raise error.User("There is no character called "+target)
	if target in defs.npc_characters: raise error.User("Can't give credits to NPCs.")
	if int(amount) == amount: raise error.User("Credit amount must be an integer.")
	if amount < 0: raise error.User("Can't give a negative amount of credits.")
	if cdata["credits"] < amount: raise error.User("Not enough credits.")
	cdata["credits"] -= amount
	tdata["credits"] += amount
	cdata.save()
	tdata.save()
