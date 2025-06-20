var group = {}

group.init = ()=>{
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
}
if(!window.no_hotload){
	group.init()
	func.init()
}