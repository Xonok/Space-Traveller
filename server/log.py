from . import io

memo = {}
def log(category,msg):
	if category not in memo:
		memo[category] = {}
	if msg in memo[category]:
		memo[category][msg] += 1
	else:
		memo[category][msg] = 1
		io.write_log(msg,category+".txt")
		# def write_log(txt,*path):
		#write a line to file