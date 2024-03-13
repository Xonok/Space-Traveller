var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var list_box = f.addElement(document.body,"div")
list_box.classList.add("vertical")
Object.entries(art.entries).sort((a,b)=>-(a[1].priority>b[1].priority)).forEach(e=>{
	var name = e[0]
	var data = e[1]
	var btn_box = f.addElement(list_box,"div")
	var btn = f.addElement(btn_box,"button",data.name)
	var box = f.addElement(list_box,"div")
	box.classList.add("vertical")
	box.style.display = "none"
	btn.onclick = ()=>{box.style.display=box.style.display==="initial" ? "none" : "initial"}
	f.addElement(box,"div",data.desc)
	Object.entries(data.concept_art||{}).forEach(a=>{
		var box2 = f.addElement(box,"div")
		box.classList.add("horizontal")
		var img = f.addElement(box2,"img")
		img.src = a[0]
		img.style.maxWidth = "200px"
		img.style.maxHeight = "200px"
		var desc = f.addElement(box2,"div",a[1])
		console.log(a[0],a[1])
	})
	console.log(name,data)
})