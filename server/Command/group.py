from . import api
from server import Group,error

def do_get_group_data(cdata):
	pass
def do_group_create(cdata,name="str"):
	return Group.create(name,cdata["name"])
def do_group_apply(cdata,group="str",reason="str"):
	return Group.apply(group,cdata["name"],reason)
def do_group_accept(cdata,name="str"):
	cname = cdata["name"]
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can accept applications.")
	return Group.accept(group["id"],name)
def do_group_deny(cdata,name="str"):
	cname = cdata["name"]
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can deny applications.")
	return Group.deny(group["id"],name)
def do_group_leave(cdata):
	cname = cdata["name"]
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	return Group.leave(group["id"],cname)
def do_group_kick(cdata,name="str"):
	cname = cdata["name"]
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can kick people.")
	return Group.kick(group["id"],name)
def do_group_transfer(cdata,new_leader="str"):
	cname = cdata["name"]
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	return Group.transfer(group["id"],new_leader)
api.register("get-group-data",do_get_group_data,"group","groups")
api.register("group-create",do_group_create,"group")
api.register("group-apply",do_group_apply,"group")
api.register("group-accept",do_group_accept,"group")
api.register("group-deny",do_group_deny,"group")
api.register("group-leave",do_group_leave,"group")
api.register("group-kick",do_group_kick,"group")
api.register("group-transfer",do_group_transfer,"group")

# def create(name,leader):
# def apply(g_id,name,reason):
# def accept(g_id,name):
# def deny():
# def leave(g_id,name):
# def transfer(g_id,new_leader):