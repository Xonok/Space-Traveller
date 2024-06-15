
function update_repair(do_reset=false){
	var stats = selected_ship.stats
	var hull_lost = stats.hull.max - stats.hull.current
	var armor_lost = stats.armor.max - stats.armor.current
	if(!do_reset && window.repair_hull_amount.value){
		hull_lost = Math.min(hull_lost,Number(window.repair_hull_amount.value))
	}
	if(!do_reset && window.repair_armor_amount.value){
		armor_lost = Math.min(armor_lost,Number(window.repair_armor_amount.value))
	}
	var tech = ship_defs[selected_ship.type].tech
	window.repair_hull_amount.value = hull_lost
	window.repair_armor_amount.value = armor_lost
	window.current_hull.innerHTML = "Hull: "+stats.hull.current+"/"+stats.hull.max
	window.current_armor.innerHTML = "Armor: "+stats.armor.current+"/"+stats.armor.max
	window.current_shield.innerHTML = "Shield: "+stats.shield.current+"/"+stats.shield.max
	window.hull_repair_cost.innerHTML = "Cost: "+f.formatNumber(repair_fees.hull*hull_lost*(tech+1))
	window.armor_repair_cost.innerHTML = "Cost: "+f.formatNumber(repair_fees.armor*armor_lost*(tech+1))
	
	//Repair all
	var total_cost = 0
	Object.entries(pships).forEach(ps=>{
		var name = ps[0]
		var data = ps[1]
		var stats = data.stats
		var hull_lost = stats.hull.max - stats.hull.current
		var armor_lost = stats.armor.max - stats.armor.current
		var tech = ship_defs[data.type].tech
		var cost = (repair_fees.hull*hull_lost+repair_fees.armor*armor_lost)*(tech+1)
		total_cost += cost
	})
	window.all_repair_cost.innerHTML = "Cost: "+f.formatNumber(total_cost)
}
function update_repair2(e){
	f.only_numbers(e)
	update_repair()
}

window.repair_hull_amount.onblur = update_repair2
window.repair_armor_amount.onblur = update_repair2
window.repair_hull.onclick = do_repair_hull
window.repair_armor.onclick = do_repair_armor
window.btn_repair_all.onclick = do_repair_all
function do_repair_hull(){
	var stats = selected_ship.stats
	var amount = Number(window.repair_hull_amount.value)
	send("repair",{"ship":selected_ship.name,"hull":amount,"armor":0})
}

function do_repair_armor(){
	var stats = selected_ship.stats
	var amount = Number(window.repair_armor_amount.value)
	send("repair",{"ship":selected_ship.name,"hull":0,"armor":amount})
}
function do_repair_all(){
	send("repair-all")
}