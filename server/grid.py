from . import io
class System(dict):
	def save(self):
		io.write2("systems",self["name"],self)
class Grid(dict):
	def __init__(self,default={},**kwargs):
		self.default = default
		self.update(kwargs)
		self.parent = None
	def set(self,x,y,value):
		x = str(x)
		y = str(y)
		if x not in self:
			self[x] = {}
		self[x][y] = value
	def get(self,x,y):
		x = str(x)
		y = str(y)
		if x not in self or y not in self[x]:
			return self.default
		return self[x][y]
	def get_all(self):
		list = []
		for column in self.values():
			for value in column.values():
				list.append(value)
		return list
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()