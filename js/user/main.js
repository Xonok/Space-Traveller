var user = {}

user.init = async()=>{
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	user.init()
}