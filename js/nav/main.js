var nav = {}

nav.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"fleet",
				"map",
				"ship",
				"terrain"
			]
		}
	}
	var files = [
		"api",
		"init"
	]

	func.load(folders,"js/nav/","folders")
	func.load(files,"js/nav/","files")
}
nav.init()
func.init_toggles()