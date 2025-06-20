from server import defs

def get(g_id):
	group = defs.groups.get(g_id)
	if not group:
		raise error.User("Invalid group ID: "+g_id)
	return group
def of_char(cname):
	group = defs.group_of.get(cname)
	return group