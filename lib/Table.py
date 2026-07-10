def get(table,default=None,*keychain):
	last = keychain[-1]
	for name in keychain[:-1]:
		table = table.get(name)
		if not table:
			if default is None:
				raise Exception("table_get failed and no default was provided. keychain: "+str(keychain))
			return default
	return table.get(last,default)
def set(table,val,*keychain):
	last = keychain[-1]
	for k in keychain[:-1]:
		if k not in table:
			table[k] = {}
		table = table[k]
	table[last] = val
def delete(table,*keychain):
	if len(keychain) == 1:
		del table[keychain[0]]
	else:
		table_del(table[keychain[0]],keychain[1:])
def clean(table):
	for k,v in list(table.items()):
		if isinstance(v,dict):
			clean(v)
		if isinstance(v,dict) or isinstance(v,list):
			if not len(v):
				del table[k]
