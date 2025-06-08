import random

def dice(amount,sides):
	amount = int(amount)
	sides = int(sides)
	total = 0
	for i in range(amount):
		total += random.randint(1, sides)
	return total	
def direction(diff_x,diff_y):
	if abs(diff_x) > abs(diff_y):
		diff_y = 0
	if abs(diff_y) > abs(diff_x):
		diff_x = 0
	diff_x = min(diff_x,1)
	diff_x = max(diff_x,-1)
	diff_y = min(diff_y,1)
	diff_y = max(diff_y,-1)
	delta = str(diff_x)+","+str(diff_y)
	directions = {
		"0,1": 0,
		"1,1": 45,
		"1,0": 90,
		"1,-1": 135,
		"0,-1": 180,
		"-1,-1": 225,
		"-1,0": 270,
		"-1,1": 315
	}
	return directions[delta]
def wavg(*args):
	#Example use:
	#wavg((20,100),(10,10),(10,20)) -> 17.692307692307693
	a = 0
	w = 0
	for val,wgt in args:
		a += val*wgt
		w += wgt
	return a/w
def f2ir(num):
	#Converts a float to int by treating the fractional part as probability.
	int_part = int(num)
	float_part = num-int_part
	if random.random() < float_part:
		int_part += 1
	return int_part
def table_add(table,val,default,*keychain):
	last = keychain[-1]
	for name in keychain[:-1]:
		if name not in table:
			table[name] = {}
		table = table[name]
	table[last] = table.get(last,default)+val
def table_get(table,default,*keychain):
	last = keychain[-1]
	for name in keychain[:-1]:
		table = table.get(name)
		if not table: return default
	return table.get(last,default)