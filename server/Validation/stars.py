from server import defs

def validate():
	for star,data in defs.systems.items():
		if star not in defs.constellation_of:
			print("Star "+star+" is not in any constellation.")
		for x,col in data["tiles"].items():
			for y,tile in col.items():
				wormhole = tile.get("wormhole")
				if wormhole:
					name = star+",WH,"+str(x)+","+str(y)
					if "target" not in wormhole:
						print("Wormhole "+name+" doesn't have a target.")
						continue
					if wormhole["target"]["system"] not in defs.systems:
						print("Target of wormhole "+name+" is an unknown system: "+wormhole["target"]["system"])
