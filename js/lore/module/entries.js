lore.entries = {
	init(){
		lore.entries.add_entries("hive","precursors","science")
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
	"hive": "A hiveminded race of individuals. Other than an instict to be loyal to the Hive, they are entirely free to think their own thoughts.<br>Technology is biological. Many items are of common precursor make too.",
	"precursors": "Mysterious people from the past. <br>Their history as known to us consists of the Mythical, High and Fall eras.<br>*The Mythical Era is when they originally rose on the planet Terra and spread through the universe.<br>*The High Era is when they were at the peak of their power and controlled the whole known universe for thousands of years, leaving many signs of their presence.<br>*The Fall Era is when they disappeared entirely over just a couple centuries. Despite it taking centuries, they apparently didn't document their fall in any format we know of.",
	"science": "Study of reality in all its forms. Notable branches include:<br>*Archaeology - the study of Precursors and other ancients.<br>New Studies - technology discovered or adapted by the current inhabitants of the universe.<br>"
}