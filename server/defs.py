from . import io,items
def read(name):
	return io.read("defs",name)
gear_types = read("gear_types")
goods = read("goods")
ships = read("ships")
planets = read("planets")
industries = read("industries")
machines = read("machines")