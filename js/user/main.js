var user = {}

user.init = ()=>{
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

	func.load(folders,"js/user/","folders")
	func.load(files,"js/user/","files")
}
if(!window.no_hotload){
	user.init()
	func.init()
}