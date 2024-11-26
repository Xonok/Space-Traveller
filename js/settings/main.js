var settings = {}

settings.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: []
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/settings/","folders")
	func.load(files,"js/settings/","files")
}
settings.init()