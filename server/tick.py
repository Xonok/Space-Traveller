import time,math,_thread
from server import defs

time_per_tick = {
	"short": 60*5, # 5 minutes
	"long": 60*60*3, # 3 hours
	"day": 60*60*24 # 24 hours
}

def ticks_since(timestamp,tick_type):
	if tick_type not in time_per_tick: raise Exception("Unknown tick type: "+tick_type)
	now = time.time()
	now_ticks = int(now//time_per_tick[tick_type])
	timestamp_ticks = int(timestamp//time_per_tick[tick_type])
	return now_ticks-timestamp_ticks
def time_until_next(tick_type):
	now = time.time()
	then = math.ceil(now/time_per_tick[tick_type])*time_per_tick[tick_type]
	return then-now
def do_every(period,f,*args):
	def g_tick():
		t = time.time()
		while True:
			t += period
			yield max(t - time.time(),0)
	g = g_tick()
	while True:
		time.sleep(next(g))
		f(*args)
last_time = time.time()
def run():
	global last_time
	ticks = ticks_since(last_time,"long")
	if ticks:
		#try to tick all structures over a 5 minute period, but no less than 1 per second
		delay = min(60*5 / len(defs.structures),1)
		last_time = time.time()
		for name,structure in list(defs.structures.items()):
			if structure["name"] in defs.structures:
				structure.tick()
			time.sleep(delay)
def init():
	_thread.start_new_thread(do_every,(time_per_tick["short"],run))