var strategy = {}

strategy.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"simplex"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/strategy/","folders")
	func.load(files,"js/strategy/","files")
}
strategy.init()
func.init()