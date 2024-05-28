var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var list_box = window.buttons
Object.entries(art.entries).sort((a,b)=>{
	if(a[1].priority>b[1].priority){
		return -1
	}
	else if(a[1].priority<b[1].priority){
		return 1
	}
}).forEach(e=>{
	var name = e[0]
	var data = e[1]
	var btn = f.addElement(list_box,"button",data.name)
	btn.style.width = "100px"
	btn.style.margin = "10px"
	var box = f.addElement(list_box,"div")
	box.classList.add("vertical")
	box.style.border = "2px solid rgb(0, 191, 255)"
	box.style.margin = "10px"
	box.style.display = "none"
	btn.onclick = ()=>{box.style.display=box.style.display==="initial" ? "none" : "initial"}
	var img_box=f.addElement(box,"div")
	img_box.classList.add("horizontal")
	img_box.style.border="1px solid rgb(0, 191, 255)"
	var img_box2=f.addElement(img_box,"div")
	img_box2.style.borderRight="2px solid rgb(0, 191, 255)"
	img_box2.style.padding="10px"
	if(data.img){
		var img = f.addElement(img_box2,"img")
		img.src = data.img
		img.style.maxHeight="200px"
		img.style.minHeight="80px"
		img.style.maxWidth="200px"
		img.style.minWidth="80px"
		img.style.marginLeft="20px"
		img.style.marginRight="20px"
	}
	var text_box=f.addElement(img_box,"div")
	text_box.classList.add("vertical")
	text_box.style.padding="5px"
	var desc=f.addElement(text_box,"div",data.desc)
	desc.style.color="lightyellow"
	var concept=f.addElement(text_box,"div",data.concept)
	concept.style.color="lightblue"
	Object.entries(data.concept_art||{}).forEach(a=>{
		var box2 = f.addElement(box,"div")
		box2.style.border="1px rgb(0, 191, 255) dotted"
		box2.style.padding="5px"
		box2.style.marginLeft="80px"
		box2.classList.add("horizontal")
		var img = f.addElement(box2,"img")
		img.src = a[0]
		img.style.maxWidth = "200px"
		img.style.maxHeight = "200px"
		var desc = f.addElement(box2,"div",a[1])
		//console.log(a[0],a[1])
	})
	//console.log(name,data)
})

function send(command,table={}){
	table.key = key
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			var image_names = Object.values(msg.images.items)
			var ship_names = Object.values(msg.images.ships)
			var all_images = [...image_names,...ship_names]
			var seen = []
			var summary = f.addElement(window.images,"div")
			summary.style.color = "white"
			var successes = 0
			var failures = 0
			var tries = 0
			all_images.forEach(i=>{
				if(seen.includes(i)){return}
				tries++
				var size = "120px"
				var box = f.addElement(window.images,"label")
				box.style.maxWidth = size
				box.style.maxHeight = size
				box.style.width = size
				box.style.height = size
				box.style.display = "inline-block"
				var img = f.addElement(box,"img")
				img.src = i
				img.style.maxWidth = size
				img.style.maxHeight = size
				img.onerror = ()=>{
					var folder = i.split("/")[0]+"/"
					var name = i.split("/")[1].split(".")[0]
					var format = "."+i.split("/")[1].split(".")[1]
					box.innerHTML = folder+"<br>"+name+"<br>"+format
					failures++
				}
				img.onload = ()=>{
					var px = img.naturalHeight*img.naturalWidth
					var kilobytes = Math.round(px*4/1024)
					var size = f.addElement(box,"label",kilobytes+"KB",true)
					if(kilobytes > 300){
						size.style.color = "red"
					}
					else if(kilobytes < 200){
						size.style.color = "green"
					}
					else{
						size.style.color = "orange"
					}
					successes++
					summary.innerHTML = "Images present: "+successes+"/"+tries
				}
				seen.push(i)
			})
			Object.values(msg.images.ships).forEach(i=>{})
		}
		else if(e.target.status===400 || e.target.status===500){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
send("get-art")