var dict = {
	removes(table,...args){
		args.forEach(a=>delete table[a])
		return table
	},
	mult(a,b){
		var result = {}
		Object.entries(a).forEach(e=>result[e[0]] = e[1]*b[e[0]])
		return result
	},
	mult2(a,n){
		var result = {}
		Object.entries(a).forEach(e=>result[e[0]] = e[1]*n)
		return result
	},
	sum(table){
		return Object.values(table).reduce((a,b)=>a+b,0)
	},
	add(table,...args){
		args.forEach(a=>{
			Object.entries(a).forEach(e=>{
				var key = e[0]
				var val = e[1]
				if(!table[key]){
					table[key] = 0
				}
				table[key] += val
			})
		})
		return table
	},
	merge(table,...args){
		args.forEach(a=>{
			Object.entries(a).forEach(e=>{
				var key = e[0]
				var val = e[1]
				table[key] = val
			})
		})
		return table
	}
}