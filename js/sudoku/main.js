var sudoku = {}

sudoku.init = async()=>{
	var folders = {
		module: {
			folders: {},
			files: [
				"puzzles"
			]
		}
	}
	var files = [
		"init"
	]

	func.load(folders,"js/sudoku/","folders")
	func.load(files,"js/sudoku/","files")
	await func.loaded()
	func.init()
}
if(!window.no_hotload){
	sudoku.init()
}