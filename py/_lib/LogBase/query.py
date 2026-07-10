import json
from . import var,api

def table_get(table,key):
	return var.tables[table][key]
def table_get_all(table):
	return var.tables[table]
def init():
	api.query_register("table-get",table_get)
	api.query_register("table-get-all",table_get_all)
