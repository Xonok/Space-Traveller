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
	window.trade.onclick=null
	window.trade.style.visibility = "hidden"
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
	if(document.documentElement.offsetHeight !== 51){
		throw new Error("Navbar height not 51")
	}
	window.frameElement.style.height = document.documentElement.offsetHeight+"px"
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
	var items = f.addElement(div,"button","Items")
	items.setAttribute("id","items")
	items.onclick=()=>change_page(items)
	var editor = f.addElement(div,"button","Editor")
	editor.setAttribute("id","editor")
	editor.onclick=()=>change_page(editor)
	var forum = f.addElement(div,"button","Forum")
	forum.setAttribute("id","forum")
	forum.onclick=()=>change_page(forum)
	var chat = f.addElement(div,"button","Chat")
	chat.setAttribute("id","chat")
	chat.onclick=()=>change_page(chat)
	f.addElement(div,"label","In Development")
	var quests = f.addElement(div,"button","Quests")
	quests.setAttribute("id","items")
	quests.onclick=()=>change_page(quests)
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