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
if(!window.no_hotload){
	profile.init()
	func.init()
}