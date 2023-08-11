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

from . import io,defs

def data(name):
	if not name in defs.characters:
		raise Exception("No character called "+name+".")
	return defs.characters[name]