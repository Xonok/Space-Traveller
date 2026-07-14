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
old_config = None
try:
	with open("config.json","r") as f:
		old_config = f.read()
		config = config | json.loads(old_config)
except FileNotFoundError as e:
	print("No config found. Creating a new one with default settings.")
except Exception as e:
	raise
print("Config:")
for key,val in config.items():
	print("\t"+key+": "+str(val))
if config["saving"]:
	new_config = json.dumps(config,indent="\t")
	if new_config != old_config:
		with open("config.json","w") as f:
			f.write(new_config)
			#json.dump(config,f,indent="\t")