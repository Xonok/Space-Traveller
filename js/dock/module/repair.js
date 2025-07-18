
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
	var tech = q.idata[selected_ship.type].tech
	window.repair_hull_amount.value = hull_lost
	window.repair_armor_amount.value = armor_lost
	window.current_hull.innerHTML = "Hull: "+stats.hull.current+"/"+stats.hull.max
	f.tooltip2(window.current_hull,"If you no repair hull, you slow.")
	window.current_armor.innerHTML = "Armor: "+stats.armor.current+"/"+stats.armor.max
	window.current_shield.innerHTML = "Shield: "+stats.shield.current+"/"+stats.shield.max
	window.hull_repair_cost.innerHTML = "Cost: "+f.formatNumber(q.repair_fees.hull*hull_lost*(tech+1))
	window.armor_repair_cost.innerHTML = "Cost: "+f.formatNumber(q.repair_fees.armor*armor_lost*(tech+1))
	
	//Repair all
	var total_cost = 0
	Object.values(q.pships).forEach(ps=>{
		var stats = ps.stats
		var hull_lost = stats.hull.max - stats.hull.current
		var armor_lost = stats.armor.max - stats.armor.current
		var tech = q.idata[ps.type].tech
		var cost = (q.repair_fees.hull*hull_lost+q.repair_fees.armor*armor_lost)*(tech+1)
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
	var amount = Number(window.repair_hull_amount.value)
	f.send("repair",{"ship_id":selected_ship.name,"hull":amount,"armor":0})
}

function do_repair_armor(){
	var amount = Number(window.repair_armor_amount.value)
	f.send("repair",{"ship_id":selected_ship.name,"hull":0,"armor":amount})
}
function do_repair_all(){
	f.send("repair-all")
}