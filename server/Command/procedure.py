from server import user,defs
from . import query
import inspect

commands = {}
command_auth = {}
command_queries = {}
queries = {}
def command(name,func,auth=True):
	commands[name] = func
	command_auth[name] = auth
def query(name,func):
	queries[name] = func
def bind(name,*args):
	command_queries[name] = args
def auth(self,name,data):
	username = user.check_key(data["key"])
	udata = defs.users.get(username)
	ctx = {
		"udata": user.check_key(data["key"]),
		"cdata": defs.characters.get(udata["active_character"]),
		"self": self
	}
	return ctx
def do_query(q,ctx):
	if q in queries:
		return queries[q](ctx)
	else:
		print("Unknown query: "+q)
	for k in inspect.getmembers(query,inspect.isfunction):
		print(k)
def process(self,data):
	self.check(data,"command")
	name = data.get("command")
	if name not in commands: return
	should_auth = command_auth[name]
	if should_auth:
		self.check(data,"command","key")
	else:
		self.check(data,"command")
	ctx = None
	if command_auth[name]:
		ctx = auth(self,name,data)
	response = commands[name](self,data,ctx)
	if not response:
		response = {}
	if name in command_queries:
		for q in command_queries[name]:
			if q not in response:
				response[q] = do_query(q,ctx)
				#print(q,response[q])
	self.send_json(response)
	return True
#data = {
#	"key": 
#	"command": 
#	"data": 
#}
