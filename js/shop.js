var happiness = ["cat","dog","chocolate","cake","coffee","book"]
var buy = window.buy_table
var sell = window.sell_table

function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){
		e.innerHTML=inner
	}
	parent.append(e)
	return e
}

addElement(buy,"th","name")
addElement(buy,"th","amount")
addElement(buy,"th","price").setAttribute("colspan","2")

addElement(sell,"th","name")
addElement(sell,"th","amount")
addElement(sell,"th","price").setAttribute("colspan","2")


happiness.forEach(h=>{
	var row = document.createElement("tr")
	addElement(row,"td",h).setAttribute("class","name")
	addElement(row,"td",0)
	addElement(row,"td",0)
	var buy_amount=addElement(row,"td")
	var input=addElement(buy_amount,"input")
	input.setAttribute("min","1")
	input.setAttribute("type","number")
	buy_amount.setAttribute("class","input")
	buy.appendChild(row)
	
	var row2 = document.createElement("tr")
	addElement(row2,"td",h).setAttribute("class","name")
	addElement(row2,"td",0)
	addElement(row2,"td",0)
	var sell_amount=addElement(row2,"td")
	var input2=addElement(sell_amount,"input")
	sell_amount.setAttribute("class","input")
	input2.setAttribute("min","1")
	input2.setAttribute("type","number")

	sell.appendChild(row2)
})
