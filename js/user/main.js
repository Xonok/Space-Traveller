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
user.init()
func.init()