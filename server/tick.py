import time,math

time_per_tick = {
	"short": 60*5, # 5 minutes
	"long": 60*60*3 # 3 hours
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
