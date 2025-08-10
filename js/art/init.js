var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

function send(command,table={}){
	table.key = key
	table.command = command
	var char = sessionStorage.getItem("char")
	if(char && !table.active_character){
		table.active_character = char
	}
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
			var item_names = Object.values(msg.images.items)
			var ship_names = Object.values(msg.images.ships)
			var landmark_names = Object.values(msg.images.landmarks)
			var wormhole_names = Object.values(msg.images.wormholes)
			var badge_names = Object.values(msg.images.badges)
			var glyph_names = Object.values(msg.images.glyphs)
			var unused_names = Object.values(msg.images.unused)
			var quest_names = []
			Object.values(msg.images.quests).forEach(q=>{
				q.forEach(i=>{
					quest_names.push(i)
				})
			})
			var all_images = [...item_names,...ship_names,...landmark_names,...wormhole_names,...badge_names,...glyph_names,...quest_names]
			var seen = []
			var box = f.addElement(window.images,"div")
			var summary = f.addElement(box,"div")
			var summary_bar = f.addElement(box,"progress")
			var counter_unused = f.addElement(box,"div")
			summary.style.color = "white"
			counter_unused.style.color = "white"
			var successes = 0
			var failures = 0
			var tries = 0
			var unused = 0
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
					box.innerHTML = ""
					var folder = i.split("/")[0]+"/"
					var name = i.split("/")[1].split(".")[0]
					var format = "."+i.split("/")[1].split(".")[1]
					var txt = folder+"<br>"+name+"<br>"+format
					var label = f.addElement(box,"label",txt,false)
					if(format===".png"){
						label.style.color = "red"
					}
					else{
						label.style.color = "white"
					}
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
					summary_bar.value = successes
					summary_bar.max = tries
					summary.innerHTML = "Images present: "+successes+"/"+tries+" (missing: "+(tries-successes)+")"
				}
				seen.push(i)
			})
			var label_unused = f.addElement(window.images,"div","Unused:")
			label_unused.style.color = "white"
			var box2 = f.addElement(window.images,"div")
			unused_names.forEach(i=>{
				var size = "120px"
				var img_box = f.img_box(box2,size,size,i)
				img_box.style.display = "inline-block"
				img_box.innerHTML += i
				unused++
			})
			counter_unused.innerHTML += "Unused: "+unused
			console.log(msg.images.unused)
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