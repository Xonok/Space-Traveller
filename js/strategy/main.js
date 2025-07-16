var strategy = {}

strategy.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"draw",
				"simplex"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/strategy/","folders")
	func.load(files,"js/strategy/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	strategy.init()
}