var config = {
	styles: document.styleSheets[0],
	apply(){
		var family = localStorage.getItem("font-family")
		if(!family){
			family = "Arial"
		}
		config.styles.insertRule("*{font-family:"+family+"}")
	}
}