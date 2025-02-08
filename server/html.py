import re,os
from server import io,config

#new setting: bundle - off, on, cache
#off - page inserts are not handled server-side
#on - page inserts processed every time a html is requested
#cache - page inserts are preprocessed on server start

cache = {}

def load(path):
	data = io.get_file_data(path,"r")
	if not config.config["bundle"]:
		return data.encode("utf-8")
	if path in cache:
		print("cache hit",path)
		return cache[path]
	print("cache miss",path)
	lines = data.splitlines()
	doctype = None
	header = []
	body = []
	in_header = False
	in_body = False
	for line in lines:
		if "DOCTYPE" in line:
			doctype = line
			continue
		if "<head>" in line:
			in_header = True
			continue
		if "<body>" in line:
			in_body = True
			continue
		if "</head>" in line:
			in_header = False
			continue
		if "</body>" in line:
			in_body = False
			continue
		if in_header:
			header.append(line)
			continue
		new_line = ""
		tags = re.findall(r'<!--.*?-->|</?[^<>]+>|[^<>]+', line)
		tag_idx = None
		did_page_insert = False
		for idx,tag in enumerate(tags):
			if idx == len(tags)-1 and did_page_insert:
				tabs = 0
				if tags[0].isspace():
					tabs = len(tags[0])
				new_line += "\t"*tabs
			classes_match = re.search(r'class="([^"]+)"', tag)
			classes = classes_match.group(1).split() if classes_match else []
			if "page_insert" in classes:
				did_page_insert = True
				tag_idx = idx
				src_match = re.search(rf'src="([^"]+)"', tag)
				src = src_match.group(1)
				new_line += tag.replace("page_insert","page_insert_done")+"\n"
				tabs = 0
				if tags[0].isspace():
					tabs = len(tags[0])-1
				extra_lines = load_html(src,header)
				for line2 in extra_lines:
					new_line += "\t"*tabs+line2+"\n"				
				continue
			new_line += tag
		if not new_line:
			new_line = line
		if in_body:
			body.append(new_line)
	data2 = doctype+"\n"
	data2 += "<html>\n"
	data2 += "\t<head>\n"
	for line in header:
		data2 += line+"\n"
	data2 += "\t</head>\n"
	data2 += "\t<body>\n"
	for line in body:
		data2 += line+"\n"
	data2 += "\t</body>\n"
	data2 += "</html>\n"
	if config.config["bundle"] == "cache":
		cache[path] = data2.encode("utf-8")
	# if "nav.html" in path:
		# with open("blah.html","w") as f:
			# f.write(data2)
	return data2.encode("utf-8")
def load_html(path,header):
	data = io.get_file_data(os.path.join(io.cwd,"html",path),"r")
	lines = data.splitlines()
	in_header = False
	in_body = False
	new_lines = []
	for line in lines:
		if "<head>" in line:
			in_header = True
			continue
		if "<body>" in line:
			in_body = True
			continue
		if "</head>" in line:
			in_header = False
			continue
		if "</body>" in line:
			in_body = False
			continue
		if in_header:
			header.append(line)
			continue
		if in_body:
			new_lines.append(line)
	return new_lines