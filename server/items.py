class Items(dict):
	def __init__(self,default=0):
		self.default = default
	def add(self,key,value):
		self[key] = self.get(key)+value
	def get(self,key):
		if key in self:
			return self[key]
		else:
			return self.default
	def remove():
		if key in self:
			del self[key]