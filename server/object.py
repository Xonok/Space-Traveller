class Object(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
