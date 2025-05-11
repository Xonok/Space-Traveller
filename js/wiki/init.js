var f=func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var msg = {}

Object.values(document.getElementsByTagName("a")).forEach(e=>{
	if(e.attributes["href"]?.nodeValue === "#"){
		e.onclick = e=>{
			e.preventDefault()
			var pname = e.target.id.replace("to_","")
			subpage(pname)
		}
	}
})
/*window.to_main.onclick = e=>{
	e.preventDefault()
	subpage("main")
}*/

var cmd,page,data
function send(command,table={},testing=false){
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
		if(testing){return}
		if(e.target.status===200){
			f.forClass("error_display",error=>{
				error.innerHTML=""
			})
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url+window.location.search
				return
			}
			msg = JSON.parse(e.target.response)
			page = msg.page
			data = msg.data
			if(command === "get-wiki-page"){
				update_wiki_page()
			}
			console.log(msg)
		}
		else if(e.target.status===400 || e.target.status===500){
			f.forClass("error_display",div=>div.innerHTML = e.target.response)
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
		first_message = false
	}
	req.send(jmsg)
}

var subpages = ["item_list","ship_list","monster_list","item","ship","monster"]
function subpage(pname){
	subpages.forEach(sp=>window["sub_"+sp].style.display = "none")
	
	window["sub_"+pname].style.display = "block"
	
	send("get-wiki-page",{"page":pname})
}
function update_wiki_page(){
	var t,el,counter
	if(page === "item_list"){
		window.sub_item_list.innerHTML = ""
		counter = f.addElement(window.sub_item_list,"div")
		counter.innerHTML = "Items: "+Object.keys(data).length
		el = f.addElement(window.sub_item_list,"table")
		t = f.make_table(el,"img","name","type","tech","size")
		t.sort("name","tech","type")
		t.update(data)
	}
	else if(page === "ship_list"){
		window.sub_ship_list.innerHTML = ""
		counter = f.addElement(window.sub_ship_list,"div")
		counter.innerHTML = "Ships: "+Object.keys(data).length
		el = f.addElement(window.sub_ship_list,"table")
		t = f.make_table(el,"img","name","faction","tech","size","room","hull","speed","agility","tracking","control","slots")
		t.sort("name","tech","faction")
		t.update(data)
	}
	else if(page === "monster_list"){
		window.sub_monster_list.innerHTML = ""
		counter = f.addElement(window.sub_monster_list,"div")
		counter.innerHTML = "Monsters: "+Object.keys(data).length
		el = f.addElement(window.sub_monster_list,"table")
		t = f.make_table(el,{"default_name":"name"},"ship","bounty","gear")
		t.sort("name","tech","type")
		t.update(data)
	}
}
