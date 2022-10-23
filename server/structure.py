class Structure(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("structures",self["name"],self)