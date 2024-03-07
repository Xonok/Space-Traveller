// items
var f = func
window.transfer_button2.onclick = do_transfer2
function do_transfer2(){
	console.log(make_list("item_ship"),make_list("item_station"))
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: make_list("item_ship")
			},
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: make_list("item_station2")
			}
		]
	}
	send("transfer",table)
}
window.transfer_credits_give.onclick = do_give_credits
function do_give_credits(){
	var give = Math.floor(Number(window.give_credits.value))
	give && send("give-credits",{"amount":give})
	window.give_credits.value = 0
}
window.transfer_credits_take.onclick = do_take_credits
function do_take_credits(){
	var take = Math.floor(Number(window.take_credits.value))
	take && send("take-credits",{"amount":take})
	window.take_credits.value = 0
}
window.store_all.onclick = do_storeall
function do_storeall(){
	var table = {
		data: [
			{
				action: "give",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: items
			}
		]
	}
	send("transfer",table)
}
window.take_all.onclick = do_takeall
function do_takeall(){
	var table = {
		data: [
			{
				action: "take",
				self: pship.name,
				other: structure.name,
				sgear: false,
				ogear: false,
				items: structure.inventory.items
			}
		]
	}
	send("transfer",table)
}
window.give_credits.onblur = f.only_numbers
window.take_credits.onblur = f.only_numbers
