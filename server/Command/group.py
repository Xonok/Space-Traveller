from . import api
from server import Group,error

def do_get_group_data(cdata):
	pass
def do_group_create(cname,name="str"):
	return Group.create(name,cname)
def do_group_apply(cname,group="str",reason="str"):
	return Group.apply(group,cname,reason)
def do_group_accept(cname,name="str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can accept applications.")
	return Group.accept(group["id"],name)
def do_group_deny(cname,name="str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can deny applications.")
	return Group.deny(group["id"],name)
def do_group_leave(cname):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	return Group.leave(group["id"],cname)
def do_group_kick(cname,name="str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("Only the leader can kick people.")
	return Group.kick(group["id"],name)
def do_group_transfer(cname,new_leader="str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	return Group.transfer(group["id"],new_leader)
def do_modify_ranks(cname,ranks="list:str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("You must be the leader to modify ranks,")
	return Group.modify_ranks(group["id"],ranks)
def do_assign_rank(cname,name="str",rank="str"):
	group = Group.of_char(cname)
	if not group:
		raise error.User("You are not in any group.")
	if group["leader"] != cname:
		raise error.User("You must be the leader to modify ranks,")
	return Group.assign_rank(group["id"],name,rank)
api.register("get-group-data",do_get_group_data,"group","groups")
api.register("group-create",do_group_create,"group")
api.register("group-apply",do_group_apply,"group")
api.register("group-accept",do_group_accept,"group")
api.register("group-deny",do_group_deny,"group")
api.register("group-leave",do_group_leave,"group")
api.register("group-kick",do_group_kick,"group")
api.register("group-transfer",do_group_transfer,"group")
api.register("group-modify-ranks",do_modify_ranks,"group")
api.register("group-assign-rank",do_assign_rank,"group")
