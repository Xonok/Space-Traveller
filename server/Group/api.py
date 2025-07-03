import copy
from server import defs,error,io
from . import query

class Group(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
		if "props" not in self:
			self["props"] = {}
	def save(self):
		io.write2("groups",self["id"],self)
	#For archival reasons, deleting groups is not a good idea.
	# def delete(self):
		# del defs.groups[self["id"]]
		# io.delete(self,"data","groups",self["id"]+".json")
def update():
	for name,data in defs.groups.items():
		if "ranks" not in data:
			data["ranks"] = {}
		if "member_rank" not in data:
			data["member_rank"] = {}
def create(name,leader):
	if leader in defs.group_of:
		raise error.User("Can't create a new group when you're still in one.")
	if not name:
		raise error.User("The name must not be empty.")
	if not all(c.isalnum() or c.isspace() or c == "-" for c in name):
		raise error.User("The name of the group should consist only of letters, numbers, spaces, and -.")
	id = str(defs.world.add_group())+ "," + name.lower()
	if id in defs.groups:
		raise error.User("The name of the group is too similar to an existing one.")
	group = Group()
	group["id"] = id
	group["name"] = name
	group["leader"] = leader
	group["members"] = [leader]
	group["applications"] = {}
	group["treasury"] = 0
	group["tax"] = 0.0
	group["ranks"] = []
	group["member_rank"] = {}
	defs.groups[id] = group
	defs.group_of[leader] = group
	group.save()
def apply(g_id,name,reason):
	if name in defs.group_of:
		raise error.User("Can't apply to join a group when you're still in one.")
	group = query.get(g_id)
	group["applications"][name] = reason
def accept(g_id,name):
	if name in defs.group_of:
		raise error.User("They've already joined a different group.")
	group = query.get(g_id)
	if name not in group["applications"]:
		raise error.User("There is no application for a character called "+name)
	del group["applications"][name]
	group["members"].append(name)
	defs.group_of[name] = group
	group.save()
def deny(g_id,name):
	group = query.get(g_id)
	if name not in group["applications"]:
		raise error.User("There is no application for a character called "+name)
	del group["applications"][name]
def leave(g_id,name):
	group = query.get(g_id)
	if group["leader"] == name and len(group["members"]) > 1:
		raise error.User("The leader of the group can't leave unless they are the last member. Transfer leadership to someone else first.")
	if name not in group["members"]:
		raise error.User("You are not in the group "+g_id+" therefore you can't leave it.")
	group["members"].remove(name)
	del defs.group_of[name]
	group.save()
def kick(g_id,name):
	group = query.get(g_id)
	if group["leader"] == name:
		raise error.User("The leader of the group can't be kicked.")
	if name not in group["members"]:
		raise error.User("That person isn't in the group.")
	group["members"].remove(name)
	del defs.group_of[name]
	group.save()
def transfer(g_id,new_leader):
	group = query.get(g_id)
	if new_leader not in group["members"]:
		raise error.User("The new leader must be in the group.")
	group["leader"] = new_leader
def modify_ranks(g_id,list_ranks):
	group = query.get(g_id)
	for key,val in group["member_rank"].items():
		if val not in list_ranks:
			raise error.User("Can't remove rank "+val+" because member "+key+" has it.")
	group["ranks"] = list_ranks
	group.save()
def assign_rank(g_id,name,rank):
	group = query.get(g_id)
	if name not in group["members"]:	
		raise error.User("No one in the group is called "+name)
	if rank not in group["ranks"]:	
		raise error.User("There is no rank called "+rank)
	group["member_rank"][name] = rank
	group.save()