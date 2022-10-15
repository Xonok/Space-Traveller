from . import items
#Stations in pardus buy up to 20 ticks of upkeep.
#Due to the price logic in pardus this is bad.

default = items.Items(**{
	"energy": 80,
	"food": 120,
	"water": 100,
	"gas": 120,
	"ore": 120,
	"metals": 400,
	"liquor": 280
})
