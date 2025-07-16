var profile = {}

profile.init = async()=>{
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
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	profile.init()
}