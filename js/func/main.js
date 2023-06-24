(function () {
	var folders = {
		module: {
			folders: {},
			files: [
				"table"
			]
		}
	}
	var files = [
		"api"
	]

	function parse(obj,path,key){
		switch(key){
			case "folders":
				Object.keys(obj).forEach(k=>{
					parse(obj[k],path+k+"\\",k)
				})
				break
			case "files":
				obj.forEach(f=>{
					var script = document.createElement("script")
					script.src = path+f+".js"
					script.async = false
					document.body.appendChild(script)
					//console.log("Filepath: "+path+f+".js")
				})
				break
			default:
				Object.keys(obj).forEach(k=>{
					parse(obj[k],path,k)
				})
				break
		}
	}

	parse(folders,"js/func/","folders")
	parse(files,"js/func/","files")
})()
