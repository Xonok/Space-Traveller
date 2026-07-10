from . import var

def check(condition,msg):
	if condition: print(msg)
def is_table(t_id):
	result = t_id in var.tables
	check(result,"Table "+t_id+" already exists.")
	return result
def not_table(t_id):
	result = t_id not in var.tables
	check(result,"Table "+t_id+" doesn't exist")
	return result
def is_none(key,val):
	result = val is None
	check(result,"Key "+key+" value is none.")
	return result
def missing(data,key):
	result = key not in data
	check(result,"Key "+key+" is missing.")
	return result