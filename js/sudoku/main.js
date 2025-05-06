var sudoku = {}

sudoku.init = ()=>{
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
}
if(!window.no_hotload){
	sudoku.init()
	func.init()
}