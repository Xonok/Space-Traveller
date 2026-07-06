def tokenize(line):
	length = len(line)
	tokens = []
	prev = 0
	cur = 0
	in_str = False
	while(cur < length):
		c = line[cur:cur+1]
		if c == "\"":
			in_str = not in_str
		if c == "," and not in_str:
			tokens.append(line[prev:cur])
			prev = cur+1
		cur += 1
	if line.endswith("\n"):
		tokens.append(line[prev:cur-1])
	else:
		tokens.append(line[prev:cur])
	for idx,t in enumerate(tokens):
		if t == "":
			tokens[idx] = None
		if t.startswith("\"") and t.endswith("\""):
			tokens[idx] = tokens[idx][1:-1]
	return tokens
def schema_parse(line):
	schema_keys = tokenize(line)
	if schema_keys[0] == None:
		print("Schema is empty.")
		return
	schema_table = {}
	for idx,key in enumerate(schema_keys):
		schema_table[key] = idx
	return schema_table
def schema_match(a,b):
	for k,v in a.items():
		if b[k] != v:
			return False
	for k,v in b.items():
		if a[k] != v:
			return False
	return True
def parse_line(line,schema=None):
	tokens = tokenize(line)
	data = {}
	for key,idx in schema.items():
		data[key] = tokens[idx]
	return data