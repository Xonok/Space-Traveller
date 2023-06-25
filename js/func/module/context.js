context = {
	data: {},
	events: {},
	receive(msg){
		var keys = []
		Object.entries(msg).forEach(e=>{
			var key = e[0]
			var val = e[1]
			var op = val.operation || "replace"
			switch(op){
				case "replace":
					context.data[key] = val
					break
				case "merge":
					context.data[key] = Object.assign(context.data[key],val)
					break
				case "append":
					context.data[key].push(val)
					break
			}
			keys.push(key)
		})
		keys.forEach(k=>{
			if(context.events[k]){
				context.events[k].forEach(e=>e(msg,context.data))
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