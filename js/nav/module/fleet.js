nav.fleet = {
	speed(){
		var speeds = []
		Object.values(pships).forEach(ps=>{
			speeds.push([ps.stats.speed,ps.stats.size])
		})
		return func.math.wavg(...speeds)
	}
}