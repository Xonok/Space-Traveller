import api,var,err

def log_restore(table):
	pass
def table_create(table):
	if err.is_table(table): return
	var.tables[table] = {}
	print("TABLE_CREATE",table)
	return True
def table_delete(table):
	if err.not_table(table): return
	delete var.tables[table]
	print("TABLE_DELETE",table)
	return True
def ref_create(table,ref):
	if err.not_table(table): return
	if var.tables[table].get(ref): raise Exception("Trying to create duplicate reference "+ref)
	var.tables[table][ref] = {}
	print("REF_CREATE",table+":"+ref)
	return True
def ref_key_set(idx,table,ref,key,val):
	if err.not_table(table): return
	if err.not_ref(table,ref): return
	if err.is_none(key,val): return
	var.tables[table][ref][key] = val
	val_print = "\""+val+"\""
	if val == "":
		val_print = "<empty string>"
	print("REF_SET",table+":"+ref+"."+key+" := "+val_print)
	return True
def ref_key_clear(idx,able,ref,key):
	pass
def init():
	api.action_register("table-create",table_create)
	api.action_register("table-delete",table_delete)
	api.action_register("ref-create",ref_create)
	api.action_register("ref-key-set",ref_key_set)
