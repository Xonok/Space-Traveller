import api

tables = {}

def table_create(action,table,ref="blah"):
	if table in tables:
		print("Table",table," already exists.")
		return
	tables[table] = {}
	print("Created table",table)
def table_set(action,table,ref,data):
	if table not in tables:
		print("table_set: unknown table",table)
		return
	if data is None:
		print("table_set: data is null. Use table_clear if this is intentional.")
		return
	tables[table][ref] = data
	data_print = "\""+data+"\""
	if data == "":
		data_print = "<empty string>"
	print(table+"["+ref+"] =",data_print)
api.register("table-create",table_create)
api.register("table-set",table_set)