from server import error

def message(self,txt):
	self.add_message(txt)
def to_battle(self):
	raise error.Battle()
def to_nav(self):
	raise error.Page()
