import json

#config
config = {
	"logging": False,
	"backend": False,
	"ssl": False,
	"saving": True,
	"cache": False,
	"bundle": False
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