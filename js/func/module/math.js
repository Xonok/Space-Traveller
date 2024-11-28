func.math = {
	wavg(...args){
		var a = 0
		var w = 0
		args.forEach(arg=>{
			var speed = arg[0]
			var weight = arg[1]
			a += speed*weight
			w += weight
		})
		return a/w
	}
}