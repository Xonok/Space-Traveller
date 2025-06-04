var prev_view
function navbar_update(view_id){
	// var pluto = false
	// if(pluto){
	var path = view_id
	console.log(view_id,q.in_battle)
	if(path==="characters"){
		// window.bar_battle.onclick = null
		window.bar_battle.style.visibility = "hidden"
		window.bar_profile.style.visibility = "hidden"
		window.bar_wiki.style.visibility = "hidden"
		window.bar_quests.style.visibility = "hidden"
		window.bar_nav.style.visibility = "hidden"
		window.bar_map.style.visibility = "hidden"
		window.bar_dock.style.visibility = "hidden"
	}
	else if(q.in_battle){
		window.bar_battle.style.visibility = "visible"
		window.bar_profile.style.visibility = "hidden"
		window.bar_wiki.style.visibility = "hidden"
		window.bar_quests.style.visibility = "hidden"
		window.bar_nav.style.visibility = "hidden"
		window.bar_map.style.visibility = "hidden"
		window.bar_dock.style.visibility = "hidden"
	}
	else{
		window.bar_battle.style.display = "none"
		window.bar_profile.style.visibility = "visible"
		window.bar_wiki.style.visibility = "visible"
		window.bar_quests.style.visibility = "visible"
		window.bar_nav.style.visibility = "visible"
		window.bar_map.style.visibility = "visible"
		window.bar_dock.style.visibility = "visible"
	}
	if(window["bar_"+path]){
		window["bar_"+path].className += " active"
	}
	if(path !== "dock"){
		window.bar_dock.style.display = "none"
	}
	// if(path === "battle"){
		// window.bar_nav.onclick = null
		// window.bar_nav.style.visibility = "hidden"
		// window.bar_dock.onclick=null
		// window.bar_dock.style.visibility = "hidden"
		// window.bar_more.onclick = null
		// window.bar_more.style.visibility = "hidden"
		// window.bar_characters.onclick = null
		// window.bar_characters.style.visibility = "hidden"
		// window.bar_settings.onclick = null
		// window.bar_settings.style.visibility = "hidden"
	// }
	
	// var prev_button
	// if(path !=="nav" && path !=="settings" && path !=="character" && window["bar_"+path]){
	// 	window["bar_"+path].style.display="initial"
	// 	prev_button=path
	// }
	// else if(prev_button && prev_button!=="nav" && prev_button !=="settings" && prev_button !=="character" ){
	// 	window["bar_"+prev_button].style.display="none"
	// }
	// }
	var id = "bar_"+view_id
	if(prev_view){
		prev_view.classList.remove("active")
	}
	if(window[id]){
		window[id].classList.add("active")
		prev_view = window[id]
	}
}
var visibility
function visible(){
	if(visibility){
		window.link_list.style.display="none"
		visibility=undefined
	}
	else{
		window.link_list.style.display="flex"
		visibility=true
	}	
}