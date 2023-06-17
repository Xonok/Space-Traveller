class Colony(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("colonies",self["name"],self)
def details():
	return {
		"current": 0,
		"min": 0,
		"max": 0,
		"change": 0
	}
def default_pop():
	table = {}
	for name in ["workers","industry","wealth","prestige","science"]:
		table[name] = details()
	return table
def bound(val,min_val,max_val):
	return max(min_val,min(val,max_val))