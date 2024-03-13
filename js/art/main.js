var art = {}

art.init = ()=>{
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

	func.load(folders,"js/art/","folders")
	func.load(files,"js/art/","files")
}
art.init()