
serious_margin = {
	rules: [],
	apply(){
		serious_margin.rules.forEach(r=>config.styles.deleteRule(r))
		serious_margin.rules = []
		if(config.serious_margin){
			console.log(config.serious_margin)
			serious_margin.rules.push(config.styles.insertRule("body {margin:"+config.serious_margin+";}"))
		}
	}
}
serious_margin.apply()