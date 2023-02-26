var path = top.window.location.pathname.split(".")[0].substring(1)
if(window[path]){
	window[path].className += " active"
	window[path].onclick = null
}
if(path !== "battle"){
	window.battle.style.display = "none"
}
if(path === "battle"){
	window.nav.onclick = null
}
function fixHeight(){
	var height = document.documentElement.offsetHeight
	if(!height){
		setTimeout(fixHeight,0.01)
		return
	}
	window.frameElement.style.height = document.documentElement.offsetHeight+"px"
}
fixHeight()
function change_page(btn){
	top.window.location.href = '/'+btn.id+'.html'+window.location.search
}