var nav = {}

nav.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"fleet",
				"input",
				"inv",
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
if(!window.no_hotload){
	nav.init()
	func.init()
}
