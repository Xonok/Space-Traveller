/*
CODE STATUS - unfinished
*Init file is missing.
*Most functionality is still in the previous system.
*/

if(!window.no_hotload){
	(function () {
		var folders = {
			module: {
				folders: {},
				files: [
					"input",
					"math",
					"query",
					"serious_margin",
					"table",
					"theme",
					"utils",
					"view"
				]
			}
		}
		var files = [
			"init"
		]

		func.load(folders,"js/func/","folders")
		func.load(files,"js/func/","files")
	})()
}
