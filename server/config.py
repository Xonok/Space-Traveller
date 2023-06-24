import json

#config
config = {
	"logging": False,
	"text_cache": 10,
	"image_cache": 30,
	"saving": True
}
try:
	with open("config.json","r") as f:
		config = config | json.load(f)
except FileNotFoundError as e:
	print("No config found. Creating a new one with default settings.")
except Exception as e:
	raise
print("Config:")
for key,val in config.items():
	print("\t"+key+": "+str(val))
if config["saving"]:
	with open("config.json","w") as f:
		json.dump(config,f,indent="\t")