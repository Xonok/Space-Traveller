var profile = {}

profile.init = ()=>{
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

	func.load(folders,"js/profile/","folders")
	func.load(files,"js/profile/","files")
}
profile.init()
func.init()