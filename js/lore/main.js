var lore = {}

lore.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"entries"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/lore/","folders")
	func.load(files,"js/lore/","files")
}
lore.init()