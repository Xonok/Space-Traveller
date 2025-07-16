var dock = {}

dock.init = async()=>{
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	dock.init()
}