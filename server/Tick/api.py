import time

def schedule_periodic(period,func):
	#currently uncancelable, but don't care.
	def g_tick():
		# t = time.time()
		t = (int(time.time() // period) + 1) * period
		while True:
			yield max(t - time.time(),0)
			t += period
	g = g_tick()
	while True:
		time.sleep(next(g))
		func()
def load_balance(period,func,data):
	count = len(data)
	if not count: return
	delta = period/count
	for entry in list(data):
		func(*entry)
		time.sleep(delta)