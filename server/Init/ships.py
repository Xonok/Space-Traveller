from server import defs
import os

def init():
	delete_ship_files()
def delete_ship_files():
	files = os.listdir(os.path.join("server","data","ships"))
	for f in files:
		f = f.replace(".json","")
		if f not in defs.ships:
			path = os.path.join("server","data","ships",f+".json")
			print("Deleting unused ship file:",path)
			os.remove(path)
