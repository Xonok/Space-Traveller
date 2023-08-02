var trade = {}

trade.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"manage"
			]
		}
	}
	var files = [
		"api",
		"init"
	]

	func.load(folders,"js/trade/","folders")
	func.load(files,"js/trade/","files")
}
trade.init()