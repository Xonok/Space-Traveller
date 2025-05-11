import inspect
from . import api
from server import error,Query

def do_query(ctx,queries="list:str"):
	for q in queries:
		if q not in queries:
			raise error.User("Unknown query "+q+".")
		if q in msg:
			raise error.User("Query "+q+" called twice.")
		signature = inspect.signature(queries[q])
		args = {}
		for name in signature.parameters:
			args[name] = ctx[name]
		msg[q] = Query.api.queries[q](**args)
api.register("query",do_query)
