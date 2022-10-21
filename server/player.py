class Player(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def space(self):
		inv = self["inventory"]
		inv["space_left"] = inv["space_max"] - inv["items"].size() - inv["gear"].size()
		return inv["space_left"]
	def save(self):
		io.write("players",self["name"],self)

from . import defs

def data(name):
	if not name in defs.players:
		raise Exception("No player called "+name+".")
	return defs.players[name]