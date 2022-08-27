var happiness = ["cats","dogs","chocolate","cake","coffee"]
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
addElement(buy,"th","price")
addElement(buy,"th","buy")

addElement(sell,"th","name")
addElement(sell,"th","amount")
addElement(sell,"th","price")
addElement(sell,"th","sell")

happiness.forEach(h=>{
	var row = document.createElement("tr")
	addElement(row,"td",h)
	addElement(row,"td",0)
	addElement(row,"td",0)
	var buy_amount=addElement(row,"td")
	addElement(buy_amount,"input")
	buy.appendChild(row)
	
	var row2 = document.createElement("tr")
	addElement(row2,"td",h)
	addElement(row2,"td",0)
	addElement(row2,"td",0)
	var sell_amount=addElement(row2,"td")
	addElement(sell_amount,"input")
	sell.appendChild(row2)
})
