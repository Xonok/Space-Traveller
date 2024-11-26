var map = {}

map.init = ()=>{
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

	func.load(folders,"js/map/","folders")
	func.load(files,"js/map/","files")
}
map.init()
func.init_toggles()