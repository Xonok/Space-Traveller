var prev_view
function navbar_update(view_id){
	var path = view_id
	if(path==="characters"){
		window.bar_battle.style.visibility = "hidden"
		window.bar_profile.style.visibility = "hidden"
		window.bar_wiki.style.visibility = "hidden"
		window.bar_quests.style.visibility = "hidden"
		window.bar_nav.style.visibility = "hidden"
		window.bar_map.style.visibility = "hidden"
		window.bar_dock.style.visibility = "hidden"
	}
	else if(q.in_battle){
		window.bar_battle.style.display = "initial"
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
	if(q.tile?.structure){
		window.bar_dock.classList.remove("disabled")
	}
	else{
		window.bar_dock.classList.add("disabled")
	}
	var id = "bar_"+view_id
	if(prev_view){
		prev_view.classList.remove("active")
	}
	if(window[id]){
		window[id].classList.add("active")
		prev_view = window[id]
	}
	else{console.log("No such button:", id)}
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