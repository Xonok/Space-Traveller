var map = {}

map.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"canvas"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/map/","folders")
	func.load(files,"js/map/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	map.init()
}