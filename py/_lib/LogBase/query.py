from . import var,api

def table_get(table,key):
	return var.tables[table][key]
def init():
	api.query_register("table-get",table_get)
