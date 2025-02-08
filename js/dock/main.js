var dock = {}

dock.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"construction",
				"items",
				"manage",
				"overview",
				"population",
				"quest",
				"repair",
				"ship",
				"station",
				"trade",
				"training",
				"transport"
			]
		}
	}
	var files = [
		"api",
		"init"
	]

	func.load(folders,"js/dock/","folders")
	func.load(files,"js/dock/","files")
}
if(!window.no_hotload){
	dock.init()
	func.init()
}