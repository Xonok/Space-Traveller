var wiki = {}

wiki.init = ()=>{
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
}
wiki.init()
func.init()