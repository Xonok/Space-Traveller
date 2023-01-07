var path = top.window.location.pathname.split(".")[0].substring(1)
window[path].className += " active"
window[path].onclick = null
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