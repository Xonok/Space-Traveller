var nav = {};

nav.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"map"
			]
		}
	}
	var files = [
		"api"
	]

	func.load(folders,"js/nav/","folders")
	func.load(files,"js/nav/","files")
}
nav.init()