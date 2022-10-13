class Grid(dict):
	def __init__(self,default={},**kwargs):
		self.default = default
		self.update(kwargs)
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