var wiki = {}

wiki.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/wiki/","folders")
	func.load(files,"js/wiki/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	wiki.init()
}