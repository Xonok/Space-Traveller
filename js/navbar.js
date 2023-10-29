/*
CODE STAGE - half-broken
Issues:
*Extensions sometimes prevent navbar from loading due to their own errors. (yomichan)
*The "More" button creates a mess instead of doing anything reasonable.
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
	window.bar_quests.onclick = null
	window.bar_quests.style.visibility = "hidden"
	window.bar_editor.onclick = null
	window.bar_editor.style.visibility = "hidden"
	window.bar_forum.onclick = null
	window.bar_forum.style.visibility = "hidden"
	window.bar_chat.onclick = null
	window.bar_chat.style.visibility = "hidden"
	if(path==="battle"){
		window.bar_characters.onclick = null
		window.bar_characters.style.visibility = "hidden"
	}
	if(path==="characters"){
		window.bar_battle.onclick = null
		window.bar_battle.style.visibility = "hidden"
	}
	window.bar_items.onclick = null
	window.bar_items.style.visibility = "hidden"
	window.bar_settings.onclick = null
	window.bar_settings.style.visibility = "hidden"
}
var div2
function more_options(){
	var div=f.addElement(parent.document.body,"div")
	div2=div
	div.style.display="none"
	div.setAttribute("id","options")
	div.style.position="absolute"
	div.style.zIndex="1000"
	f.addElement(div,"label","Create")
	var items = f.addElement(div,"a","Items")
	items.setAttribute("id","items")
	items.href = "items.html"
	var editor = f.addElement(div,"a","Editor")
	editor.setAttribute("id","editor")
	editor.href = "editor.html"
	var forum = f.addElement(div,"a","Forum")
	forum.setAttribute("id","forum")
	forum.href = "forum.html"
	var chat = f.addElement(div,"a","Chat")
	chat.setAttribute("id","chat")
	chat.href = "chat.html"
	f.addElement(div,"label","In Development")
	var quests = f.addElement(div,"a","Quests")
	quests.setAttribute("id","quests")
	quests.href = "quests.html"
}
var visibility
function visible(){
		if(visibility){
			div2.style.display="none"
			visibility=undefined
		}
		else{
			div2.style.display="flex"
			visibility=true
		}	
	// }
}