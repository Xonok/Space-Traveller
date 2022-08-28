var happiness = ["cat","dog","chocolate","cake","coffee","book"]

function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function make_table(name){
	var parent = window[name+"_table"]
	addElement(parent,"th","name")
	addElement(parent,"th","amount")
	addElement(parent,"th","price").setAttribute("colspan","2")
	happiness.forEach(h=>{
		var row = document.createElement("tr")
		addElement(row,"td",h).setAttribute("class","name")
		addElement(row,"td",0)
		addElement(row,"td",0)
		var amount=addElement(row,"td")
		var input=addElement(amount,"input")
		amount.setAttribute("class","input")
		input.setAttribute("class",name+"_input")
		input.item=h
		input.setAttribute("min","1")
		input.setAttribute("type","number")
		parent.appendChild(row)
	})
}
make_table("buy")
make_table("sell")

