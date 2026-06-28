import var,api

def table_get(table,ref,key="*"):
	if key == "*":
		return var.tables[table][ref]
	else:
		return var.tables[table][ref][key]
def init():
	api.query_register("table-get",table_get)
