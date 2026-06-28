import api,var,err

def table_create(table):
	if err.is_table(table): return
	var.tables[table] = {}
	print("TABLE_CREATE",table)
	return True
def ref_create(table,ref):
	if err.not_table(table): return
	var.tables[table][ref] = {}
	print("REF_CREATE",table+":"+ref)
	return True
def ref_set(table,ref,key,val):
	if err.not_table(table): return
	if err.not_ref(table,ref): return
	if err.is_none(key,val): return
	var.tables[table][ref][key] = val
	val_print = "\""+val+"\""
	if val == "":
		val_print = "<empty string>"
	print("REF_SET",table+":"+ref+"."+key+" := "+val_print)
	return True
def init():
	api.action_register("table-create",table_create)
	api.action_register("ref-create",ref_create)
	api.action_register("ref-set",ref_set)
