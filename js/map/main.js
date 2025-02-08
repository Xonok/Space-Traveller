var map = {}

map.init = ()=>{
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
}
if(!window.no_hotload){
	map.init()
	func.init()
}