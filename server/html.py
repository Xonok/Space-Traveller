import re,os
from server import io,config,cache

#new setting: bundle - true, false
#true - page inserts processed every time a html is requested
#false - page inserts are not handled server-side

pagecache = {}

def load(path):
	data = io.get_file_data(path,"r",encoding="utf-8")
	if not config.config["bundle"]:
		return data.encode("utf-8")
	if path in pagecache:
		return pagecache[path]
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
				extra_lines = load_html(src,header,body,tabs)
				for line2 in extra_lines:
					new_line += "\t"*tabs+line2+"\n"				
				continue
			new_line += tag
		if not new_line:
			new_line = line
		if in_body:
			body.append(new_line)
	pagename = os.path.basename(path).replace(".html","")
	scripts_folder = pagename
	modules_folder = os.path.join(scripts_folder,"module")
	data2 = doctype+"\n"
	data2 += "<html>\n"
	data2 += "\t<head>\n"
	no_hotload_added = False
	scripts = []
	for line in header:
		if "/main.js" in line:
			src = line.split('"')[1]
			folder = src.split("/")[1]
			scripts_folder = folder
			modules_folder = os.path.join(scripts_folder,"module")
			def filter_func(path):
				if ".js" in path:
					return True
			scripts_path = os.path.join(io.cwd,"js",scripts_folder)
			modules_path = os.path.join(io.cwd,"js",modules_folder)
			files = []
			files2 = []
			if os.path.exists(scripts_path) and os.path.isdir(scripts_path):
				files = os.listdir(scripts_path)
			if os.path.exists(modules_path) and os.path.isdir(modules_path):
				files2 = os.listdir(modules_path)
			files = list(filter(filter_func,files))
			files2 = list(filter(filter_func,files2))
			if len(files) or len(files2):
				if not no_hotload_added:
					scripts.append("\t\t"+'<script src="js/no_hotload.js" defer></script>\n')
					# data2 += "\t\t"+'<script src="js/no_hotload.js" defer></script>\n'
					no_hotload_added = True
				if "main.js" in files:
					scripts.append("\t\t"+'<script src="js/'+folder+"/"+"main.js"+'" defer></script>\n')
					# data2 += "\t\t"+'<script src="js/'+folder+"/"+"main.js"+'" defer></script>\n'
				for name in files2:
					scripts.append("\t\t"+'<script src="js/'+folder+"/module/"+name+'" defer></script>\n')
					# data2 += "\t\t"+'<script src="js/'+folder+"/module/"+name+'" defer></script>\n'
				if "init.js" in files:
					scripts.append("\t\t"+'<script src="js/'+folder+"/"+"init.js"+'" defer></script>\n')
					# data2 += "\t\t"+'<script src="js/'+folder+"/"+"init.js"+'" defer></script>\n'
				
		else:
			if "<script" in line:
				scripts.append(line)
			else:
				data2 += line+"\n"
	script_data = ""
	scripts_seen = {}
	for line in scripts:
		if "<!--" in line: continue
		src = line.split('"')[1]
		if src in scripts_seen: continue
		scripts_seen[src] = True
		script_data += io.get_file_data(os.path.join(io.cwd,src),"r",encoding="utf-8")+"\n"
	script_data += io.get_file_data(os.path.join(io.cwd,"js/pageinit.js"),"r",encoding="utf-8")+"\n"
	cache.cache[os.path.join(io.cwd,"js",pagename+"_script.js")] = script_data.encode("utf-8")
	data2 += "\t\t"+'<script src="js/'+pagename+'_script.js" defer></script>\n'
	
	# if no_hotload_added:
		# data2 += "\t\t"+'<script src="js/pageinit.js" defer></script>\n'
	data2 += "\t</head>\n"
	data2 += "\t<body>\n"
	for line in body:
		data2 += line+"\n"
	data2 += "\t</body>\n"
	data2 += "</html>\n"
	if config.config["cache"]:
		pagecache[path] = data2.encode("utf-8")
	cache_html_path = os.path.join("_cache",pagename+".html")
	cache_js_path = os.path.join("_cache",pagename+".js")
	io.check_dir(cache_html_path)
	io.check_dir(cache_js_path)
	with open(cache_html_path,"w",encoding="utf-8") as f:
		f.write(data2)
	with open(cache_js_path,"w",encoding="utf-8") as f:
		f.write(script_data)
	return data2.encode("utf-8")
def load_html(path,header,body,prev_tabs):
	data = io.get_file_data(os.path.join(io.cwd,"html","comp",path),"r",encoding="utf-8")
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
					tabs = len(tags[0])-1+prev_tabs
				extra_lines = load_html(src,header,body,tabs)
				for line2 in extra_lines:
					new_line += "\t"*tabs+line2+"\n"
				new_line += "\t"
				continue
			new_line += tag
		if not new_line:
			new_line = line
		if in_body:
			new_lines.append(new_line)
	return new_lines