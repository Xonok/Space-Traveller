from . import var,api

def table_get(table,ref):
	return var.tables[table][ref]
def ref_key_get(table,ref,key):
	return var.tables[table][ref][key]
def init():
	api.query_register("table-get",table_get)
	api.query_register("ref-key-get",ref_key_get)