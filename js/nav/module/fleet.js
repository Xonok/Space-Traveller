nav.fleet = {
	speed(){
		var speeds = []
		Object.values(pships).forEach(ps=>{
			if(cdata.ships.includes(ps.name)){
				speeds.push([ps.stats.speed,ps.stats.size])
			}
		})
		return func.math.wavg(...speeds)
	}
}