class Player(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def ship(self):
		return self["ship"]
	def save(self):
		io.write2("players",self["name"],self)

from . import io,items,defs

def data(name):
	if not name in defs.players:
		raise Exception("No player called "+name+".")
	return defs.players[name]