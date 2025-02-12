query = {
	data: {},
	events: {},
	receive(msg){
		Object.entries(msg).forEach(e=>query.data[e[0]] = e[1])
		Object.keys(msg).forEach(k=>{
			if(query.events[k]){
				query.events[k].forEach(e=>e(msg,query.data))
			}
		})
	},
	register(func,...names){
		names.forEach(n=>{
			if(!events[n]){events[n] = []}
			events[n].append(func)
		})
	}
}
var q = query.data