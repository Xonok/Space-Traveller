forClass("tablinks",e=>{
	e.onclick = open_tab
})
forClass("tabcontent",el=>{
	el.style.display = "none"
})

function open_tab(e) {
	var tabName = e.target.innerHTML
	active = e
	forClass("tabcontent",el=>{
		el.style.display = "none"
	})
	forClass("tablinks",el=>{
		el.className = el.className.replace(" active", "")
	})
	document.getElementById(tabName).style.display = ""
	e.currentTarget.className += " active"
	if(tabName!=="Trade"){
		window.itemtabs.setAttribute("style","display: none")
	}
	else{window.itemtabs.setAttribute("style","display: block")}
}
