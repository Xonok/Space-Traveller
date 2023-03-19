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
}
function fixHeight(){
	if(document.documentElement.offsetHeight !== 51){
		throw new Error("Navbar height not 51")
	}
	window.frameElement.style.height = document.documentElement.offsetHeight+"px"
}
var ready = document.readyState !== 'loading'
var listener = ()=>document.addEventListener('DOMContentLoaded', fixHeight)
ready ? fixHeight() : listener()
function change_page(btn){
	top.window.location.href = '/'+btn.id+'.html'+window.location.search
}