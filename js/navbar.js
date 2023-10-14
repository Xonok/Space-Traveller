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
	window[path].className += " active"
	window[path].onclick = null
}
if(path !== "battle"){
	window.battle.style.display = "none"
}
if(path === "battle"||path==="characters"){
	window.nav.onclick = null
	window.nav.style.visibility = "hidden"
	window.dock.onclick=null
	window.dock.style.visibility = "hidden"
	window.quests.onclick = null
	window.quests.style.visibility = "hidden"
	window.editor.onclick = null
	window.editor.style.visibility = "hidden"
	window.forum.onclick = null
	window.forum.style.visibility = "hidden"
	window.chat.onclick = null
	window.chat.style.visibility = "hidden"
	if(path==="battle"){
		window.characters.onclick = null
		window.characters.style.visibility = "hidden"
	}
	if(path==="characters"){
		window.battle.onclick = null
		window.battle.style.visibility = "hidden"
	}
	window.items.onclick = null
	window.items.style.visibility = "hidden"
	window.settings.onclick = null
	window.settings.style.visibility = "hidden"
}
function fixHeight(){
	window.insert_navbar.style.height = document.documentElement.offsetHeight+"px"
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
function update_parent(){
	fixHeight()
	more_options()
}
var ready = document.readyState !== 'loading'
var listener = ()=>document.addEventListener('DOMContentLoaded', fixHeight)
ready ? update_parent() : listener()
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