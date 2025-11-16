var defs = {}

defs.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
			]
		}
	}
	var files = [
		"api",
		"init"
	]

	func.load(folders,"js/defs/","folders")
	func.load(files,"js/defs/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	defs.init()
}
