var group = {}

group.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"display"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/group/","folders")
	func.load(files,"js/group/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	group.init()
}