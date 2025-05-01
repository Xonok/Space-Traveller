nav.fleet = {
	speed(){
		var speeds = []
		Object.values(q.pships).forEach(ps=>{
			if(q.cdata.ships.includes(ps.name)){
				speeds.push([ps.stats.speed,ps.stats.size])
			}
		})
		return func.math.wavg(...speeds)
	}
}