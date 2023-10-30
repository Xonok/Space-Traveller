/*
CODE STAGE - half-broken
Issues:
*Extensions sometimes prevent navbar from loading due to their own errors. (yomichan)
*"Dock" works when it shouldn't, which results in 2 redirects and nothing really changing.
Don't fix it - big changes incoming. Stations will move to "hot ships near you" and the dock button will be there instead.
*/

var f=func
var path = top.window.location.pathname.split(".")[0].substring(1)
if(window[path]){
	window["bar_"+path].className += " active"
	window[path].onclick = null
}
if(path !== "battle"){
	window.bar_battle.style.display = "none"
}
if(path === "battle"||path==="characters"){
	window.bar_nav.onclick = null
	window.bar_nav.style.visibility = "hidden"
	window.bar_dock.onclick=null
	window.bar_dock.style.visibility = "hidden"
	window.bar_more.onclick = null
	window.bar_more.style.visibility = "hidden"
	if(path==="battle"){
		window.bar_characters.onclick = null
		window.bar_characters.style.visibility = "hidden"
	}
	if(path==="characters"){
		window.bar_battle.onclick = null
		window.bar_battle.style.visibility = "hidden"
	}
	window.bar_settings.onclick = null
	window.bar_settings.style.visibility = "hidden"
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