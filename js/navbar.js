var path = top.window.location.pathname.split(".")[0].substring(1)
window[path].className += " active"
window[path].onclick = null
if(document.readyState !== "loading"){
	window.frameElement.style.height = document.documentElement.offsetHeight+"px"
}
else{
	document.addEventListener('DOMContentLoaded',()=>{
		window.frameElement.style.height = document.documentElement.offsetHeight+"px"
	})
}
function change_page(btn){
	top.window.location.href = '/'+btn.id+'.html'+window.location.search
}