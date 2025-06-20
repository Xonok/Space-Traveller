from . import api
from server import defs,Group

def get_group(cdata):
	return Group.of_char(cdata["name"])
def get_groups():
	return defs.groups

api.register_query("group",get_group)
api.register_query("groups",get_groups)
