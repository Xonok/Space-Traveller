lore.entries = {
	boxes: {},
	init(){
		lore.entries.add_entries("Hive","Precursors","Science")
	},
	add_button(name){
		if(lore.entries.boxes[name]){return}
		var parent = window.entries
		var box = f.addElement(parent,"div")
		lore.entries.boxes[name] = box
		var btn = f.addElement(box,"button",name)
		btn.onclick = ()=>{
			btn.onclick = null
			send("request-lore",{"name":name})
		}
	},
	add_content(name,data){
		if(!lore.entries.boxes[name]){return}
		f.addElement(lore.entries.boxes[name],"div",f.formatString(data))
	},
	add_entries(...names){
		names.forEach(lore.entries.add_entry)
	},
	add_entry(name){
		var parent = window.entries
		var txt = lore.entries[name]
		if(!txt){throw Error("Missing lore entry: "+name)}
		var box = f.addElement(parent,"div")
		//TODO: Make the outline class or otherwise make each lore entry look separate.
		box.classList.add("outline")
		f.addElement(box,"h3",name)
		f.addElement(box,"div",txt)
	},
	"Hive": "A hiveminded race of individuals. Other than an instict to be loyal to the Hive, they are entirely free to think their own thoughts.<br>Technology is biological. Many items are of common precursor make too.<br>Historically they didn't write things down, so the past of the Hive is not clear. One thing is known however - they were created by Precursors.<br>The original Hive homeworld is no longer known.<br>Got to space by using Precursor technology.",
	"Precursors": "Mysterious people from the past. <br>Their history as known to us consists of the Mythical, High and Fall eras.<br>*The Mythical Era is when they originally rose on the planet Terra and spread through the universe.<br>*The High Era is when they were at the peak of their power and controlled the whole known universe for thousands of years, leaving many signs of their presence.<br>*The Fall Era is when they disappeared entirely over just a couple centuries. Despite it taking centuries, they apparently didn't document their fall in any format we know of.",
	"Science": "Study of reality in all its forms. Notable branches include:<br>*Archaeology - the study of Precursors and other ancients.<br>New Studies - technology discovered or adapted by the current inhabitants of the universe.<br>",
	"Ark Corporation": "A company that went to space to save their homeworld. They failed to save it, but evacuated many people from a robot apocalypse that started when an alien probe was researched to discover the technology used to made it.<br>Hadn't been in space much before the Probe arrived. Had only recently discovered Precursor tech, since it wasn't on their homeworld.<br>The probe wasn't made by Precursors, but by a different advanced race that rose long after the Precursor disappearance.",
	"Exotic Matter": "An extremely energetic form of matter. Despite its vast energy it somehow doesn't spontaneously turn into light.<br>Very difficult to harvest, but the Precursors left generous stockpiles of it, so it should not run out in the foreseeable future."
}