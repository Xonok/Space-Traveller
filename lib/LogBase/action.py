import json
from . import api,var,err

def table_load(table,val):
	#Possibly unneeded
	if err.is_table(table): return
	var.tables[table] = json.loads(val)
def table_create(table):
	if err.is_table(table): return
	var.tables[table] = {}
	print("TABLE_CREATE",table)
	return True
def table_delete(table):
	if err.not_table(table): return
	del var.tables[table]
	print("TABLE_DELETE",table)
	return True
def table_set(table,key,val):
	if err.not_table(table): return
	if err.is_none(key,val): return
	var.tables[table][key] = val
	val_print = "\""+val+"\""
	if val == "":
		val_print = "<empty string>"
	print("TABLE_SET",table+":"+key+" := "+val_print)
	return True
def table_unset(table,key):
	if err.not_table(table): return
	del var.tables[table][key]
	print("TABLE_UNSET",table+":"+key)
def init():
	api.action_register("table-load",table_load)
	api.action_register("table-create",table_create)
	api.action_register("table-delete",table_delete)
	api.action_register("table-set",table_set)
	api.action_register("table-unset",table_unset)
