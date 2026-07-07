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
	if tokens[0] == None:
		print("Line is empty")
		return
	data = {}
	for key,idx in schema.items():
		data[key] = tokens[idx]
	return data
def serialize(*args):
	len_args = len(args)
	line = ""
	for idx,t in enumerate(args):
		if type(t) == str and " " in t:
			line += "\""+t+"\""
		else:
			line += t
		if idx < len_args-1:
			line += ","
	line += "\n"
	return line
def write_line(path_log,schema,**data):
	print("write_line")
	#TODO: split out the serialization into a function that only takes a list of params.s
	print("schema",schema,"data",data)
	len_schema = len(schema)
	tokens = [0] * len_schema
	idx_max = float("inf")
	idx_min = 0
	for k,v in data.items():
		idx = schema.get(k)
		if idx == None:
			print("Unknown key",k)
			continue
		idx_min = min(idx_min,idx)
		idx_max = max(idx_max,idx)
		tokens[idx] = v
	line = serialize(*tokens)
	print("line",line,"tokens",tokens)
	if len(line)>1:
		with open(path_log,"a") as f:
			f.write(line)
	print("TOKENS",tokens)
def truncate(path_log,lines):
	print("truncate","path_log",path_log,"lines",lines)
	with open(path_log,"r+") as f:
		for i in range(lines):
			print(f.readline())
			print("tell",f.tell())
		f.truncate(f.tell())