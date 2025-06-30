from . import api
from server import defs,Group

def get_group(cdata):
	return Group.of_char(cdata["name"])
def get_groups():
	output = {}
	for name,data in defs.groups.items():
		if len(data["members"]):
			output[name] = data
	return output

api.register_query("group",get_group)
api.register_query("groups",get_groups)
