var dock = {}

dock.init = ()=>{
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

	func.load(folders,"js/dock/","folders")
	func.load(files,"js/dock/","files")
}
dock.init()