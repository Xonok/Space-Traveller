var lore = {}

lore.init = async()=>{
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	lore.init()
}