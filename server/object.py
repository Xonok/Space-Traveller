class Object(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("objects",self["name"],self)