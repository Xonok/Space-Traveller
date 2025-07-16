var settings = {}

settings.init = async()=>{
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	settings.init()
}