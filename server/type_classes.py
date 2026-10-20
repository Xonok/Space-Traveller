classes = {}

def register_class(name,cls):
	classes[name] = cls
def get_class(name):
	return classes.get(name)
