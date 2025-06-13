func.time = {
	offset: Infinity,
	recv(msg,send_time){
		var t0 = send_time
		var t1 = msg.accept_time
		var t2 = msg.response_time
		var t3 = Date.now()/1000
		var rtt = (t3-t0)-(t2-t1) //round trip time, currently unused
		var off = ((t1-t0)+(t2-t3))/2
		if(isNaN(off)){return}
		func.time.offset = Math.min(func.time.offset,off)
	},
	now(){
		return Date.now()/1000+func.time.offset
	}
}