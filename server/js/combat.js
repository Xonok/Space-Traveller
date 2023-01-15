module = {
	make_scale(max,soak,resist){
		return {
			"max": max,
			"current": max,
			"soak": soak,		//Flat damage reduction
			"resist": resist	//Percent damage reduction
		}
	}
}
