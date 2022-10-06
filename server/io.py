import os,json

cwd = os.getcwd()

def write(fname,table):
	with open(fname,"w") as f:
		f.write(json.dumps(table))
def read(fname):
	try:
		with open(fname,"r") as f:
			return json.loads(f.read())
	except:
		return {}
def get_file_data(path):
	with open(path,"rb") as f:
		return f.read()