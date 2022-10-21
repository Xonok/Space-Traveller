from . import io,items,types,user
def read(name):
	return io.read2("defs",name)
def make_dict(keys,folder,typename):
	table = {}
	for e in keys:
		table[e] = types.read(folder,e,typename)
	return table

#Constants
gear_types = read("gear_types")
goods = read("goods")
ships = read("ships")
planets = read("planets")
industries = read("industries")
machines = read("machines")

#Mutable
players = make_dict(user.get_all(),"players","player")
systems = {}
systems["Ska"] = types.read("systems","Ska","system")