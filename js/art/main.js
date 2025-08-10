var art = {}

art.init = ()=>{
	var folders = {
		module: {
			folders: {},
			files: []
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/art/","folders")
	func.load(files,"js/art/","files")
}
if(!window.no_hotload){
	art.init()
	func.init()
}