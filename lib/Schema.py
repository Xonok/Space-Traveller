def check(msg,err,*args):
	for arg in args:
		if not arg in msg:
			raise err("Missing required \""+arg+"\"")