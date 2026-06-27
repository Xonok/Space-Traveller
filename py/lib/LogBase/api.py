#A database based on storing changes to dictionaries into logs.

"""
Immediate concerns:
*Create, delete, update a dictionary.
*Append to log.
*Read log from disk and redo operations.

Later:
*Schemas, validation, transactions, log rotation
"""

#Start with a pregenerated log.
#For testing purposes, keep everything in the same folder for now and run this file alone.

import io,inspect

commands = {}
command_args = {}

def csv_split(txt):
	length = len(txt)
	tokens = []
	prev = 0
	cur = 0
	in_str = False
	while(cur < length):
		c = txt[cur:cur+1]
		if c == "\"":
			in_str = not in_str
		if c == "," and not in_str:
			tokens.append(txt[prev:cur])
			prev = cur+1
		cur += 1
	if txt.endswith("\n"):
		tokens.append(txt[prev:cur-1])
	else:
		tokens.append(txt[prev:cur])
	for idx,t in enumerate(tokens):
		if t == "":
			tokens[idx] = None
		if t.startswith("\"") and t.endswith("\""):
			tokens[idx] = tokens[idx][1:-1]
	return tokens
def restore(fname):
	global tables
	try:
		with open(fname,"r") as f:
			schema_keys = csv_split(f.readline())
			schema_table = {}
			for idx,key in enumerate(schema_keys):
				schema_table[key] = idx
			for line in f.readlines():
				tokens = csv_split(line)
				data = {}
				for key,idx in schema_table.items():
					data[key] = tokens[idx]
				#action,table,ref,data = tokens
				
				run(**data,commit=False)
	except:
		print("Failed to restore DB from disk.")
		raise
def register(cmd_name,func):
	if cmd_name in commands:
		print("Duplicate command:",cmd_name)
		return
	if not func:
		print("func not provided")
	commands[cmd_name] = func
	spec = inspect.signature(func).parameters
	command_args[cmd_name] = list(spec)
def run(action,table,ref,data,commit=False):
	if action not in commands:
		print("Unknown action",action)
		return
	args_in = {}
	cmd_args = command_args[action]
	if "action" in cmd_args:
		args_in["action"] = action
	if "table" in cmd_args:
		args_in["table"] = table
	if "ref" in cmd_args:
		args_in["ref"] = ref
	if "data" in cmd_args:
		args_in["data"] = data
	
	commands[action](**args_in)
