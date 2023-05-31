var config = {
	styles: document.styleSheets[0],
	apply(){
		var family = localStorage.getItem("settings:font")
		if(!family){
			family = "Arial"
		}
		config.styles.insertRule("*{font-family:"+family+"}")
	}
}