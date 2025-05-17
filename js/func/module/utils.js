func.utils = {
	load_page_inserts(){
		func.forClass("page_insert",e=>{
			func.utils.load(e.getAttribute("src"),e)
		})
	},
	load(url,el){
		return new Promise((resolve,reject)=>{
			var options = {}
			if(url.endsWith(".html")){
				options.headers = new Headers({'content-type': 'text/html'})
			}
			fetch(url,options)
			.then(response=>{
				response.text().then(html=>{
					var doc = new DOMParser().parseFromString(html, 'text/html')
					var list = [].concat(Array.from(doc.head.children),Array.from(doc.body.children))
					list.forEach(e=>{
						if(e.nodeName == "SCRIPT" && e.src){
							window.less = {
								logLevel: 2,
								async: true,
								fileAsync: true
							}
							var script = document.createElement("script")
							script.src = e.src
							e = script
						}
						el.appendChild(e)
					})
					resolve()
				})
			})
			.catch(error=>{
				console.log(error)
				reject()
			})
		})
	}
}
