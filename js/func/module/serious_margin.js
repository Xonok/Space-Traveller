
serious_margin = {
	apply(){
		config.serious_margin && config.styles.insertRule("body {margin:"+config.serious_margin+";}")
	}
}
serious_margin.apply()