config.apply()
var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

window.retreat.onclick = do_retreat
window.attack.onclick = do_attack

function send(command,table={}){
	table.key = key
	table.command = command
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
			update_ships(msg,"ally",0)
			update_ships(msg,"enemy",1)
			update_log(msg,window.log_ally,0)
			update_log(msg,window.log_enemy,1)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = "Server error."
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function update_ships(msg,blah,nr){
	var cdata = msg.cdata
	var battle = msg.battle
	var weapons_info={}
	const add = (list,item,amount)=>{
		if(!list[item]){list[item] = 0}
		list[item] += amount
	}
	//ally
	var weapons = {}
	var drones = {}
	window[String(blah+"_ships")].innerHTML = ""
	window[String(blah+"_stats")].innerHTML = ""
	window[String("missile_"+blah)].innerHTML = ""
	f.headers(window[String(blah+"_ships")],"owner","ship","hull","armor","shield")
	// Object.values(msg.battle.sides[nr].drones/missiles).forEach(d=>{
		
	// })
	Object.values(msg.battle.sides[nr].combat_ships).forEach(s=>{
		Object.entries(s.weapons).forEach(w=>{
			weapons_info[w[0]]=w[1]
			add(weapons,w[0],w[1].amount)
		})
		s=s.ship
		var hull = s.stats.hull.current+"/"+s.stats.hull.max
		var armor = s.stats.armor.current+"/"+s.stats.armor.max
		var shield = s.stats.shield.current+"/"+s.stats.shield.max
		row(window[String(blah)+"_ships"],s.owner,s.custom_name||s.name,hull,armor,shield)
	})
	var weapon_count = 0
	var attacks = 0
	var damage = 0
	Object.entries(weapons).forEach(w=>{
		var name = w[0]
		var count = w[1]
		weapon_count += count
		attacks += count*weapons_info[name].shots
		damage += count*weapons_info[name].shots*weapons_info[name].damage
		window[String(blah)+"_stats"].innerHTML+="</br>"+weapons_info[name].name+" x"+count
	})
	window[String(blah)+"_stats"].innerHTML+="</br></br> Total weapons: "+weapon_count
	window[String(blah)+"_stats"].innerHTML+="</br> Total attacks: "+attacks
	window[String(blah)+"_stats"].innerHTML+="</br> Maximum damage: "+damage
	// window[String("missile_"+blah)].innerHTML
}
function update_log(msg,parent,number){
	parent.innerHTML = ""
	Object.values(msg.battle.sides[number].logs.reverse()).forEach(v=>{
		v.forEach(m=>f.addElement(parent,"label",m.msg))
		
	})
}
function row(parent,...data){
	var r = f.addElement(parent,"tr")
	data.forEach(d=>f.addElement(r,"td",d))
}
function do_attack(){
	send("attack",{"rounds":1})
}
function do_retreat(){
	send("retreat")
}

send("update-battle")