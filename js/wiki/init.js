
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

var subpages = ["item_list","ship_list","monster_list","item","ship","monster"]
function subpage(pname){
	subpages.forEach(sp=>window["sub_"+sp].style.display = "none")
	
	window["sub_"+pname].style.display = "block"
	
	f.send("get-wiki-page",{"page":pname})
}
function update_wiki_page(){
	var t,el,counter
	if(q.page === "item_list"){
		window.sub_item_list.innerHTML = ""
		counter = f.addElement(window.sub_item_list,"div")
		counter.innerHTML = "Items: "+Object.keys(q.data).length
		el = f.addElement(window.sub_item_list,"table")
		t = f.make_table(el,"img","name","type","tech","size")
		t.sort("name","tech","type")
		t.update(q.data)
	}
	else if(q.page === "ship_list"){
		window.sub_ship_list.innerHTML = ""
		counter = f.addElement(window.sub_ship_list,"div")
		counter.innerHTML = "Ships: "+Object.keys(q.data).length
		el = f.addElement(window.sub_ship_list,"table")
		t = f.make_table(el,"img","name","faction","tech","size","room","hull","speed","agility","tracking","control","slots")
		t.sort("name","tech","faction")
		t.update(q.data)
	}
	else if(q.page === "monster_list"){
		window.sub_monster_list.innerHTML = ""
		counter = f.addElement(window.sub_monster_list,"div")
		counter.innerHTML = "Monsters: "+Object.keys(q.data).length
		el = f.addElement(window.sub_monster_list,"table")
		t = f.make_table(el,{"default_name":"name"},"ship","bounty","gear")
		t.sort("name","tech","type")
		t.update(q.data)
	}
}

function wiki_open(){}
function wiki_message(msg){
	if(msg.page){
		update_wiki_page()
	}
}

f.view.register("wiki",wiki_open,wiki_message)
