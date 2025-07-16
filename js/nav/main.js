var nav = {}

nav.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"fleet",
				"input",
				"inv",
				"map",
				"ship",
				"starmap",
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	nav.init()
}
