from . import gear
types = {
	"harvester": {
		"space": 70,
		"slots": {
			"gun": 1
		},
		"guns": 1,
		"hull": 50,
		"speed": 90,
		"agility": 40,
		"img": "harvester.png",
		"desc": "Workhorse of the hive, a great all-purpose freighter for those starting out."
	},
	"striker": {
		"space": 40,
		"slots": {
			"gun": 3
		},
		"hull": 60,
		"speed": 60,
		"agility": 70,
		"img": "clipart2908532.png",
		"desc": "Gun-heavy brawler, relying on its agility to survive combat."
	}
}
def slots(name,gtype):
	if gtype not in types[name]["slots"]:
		return 99999
	return types[name]["slots"][gtype]
def slots_left(name,gtype,pgear):
	equipped = gear.equipped(gtype,pgear)
	max = slots(name,gtype)
	return max-equipped