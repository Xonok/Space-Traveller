var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var list_box = window.buttons
Object.entries(art.entries).sort((a,b)=>-(a[1].priority>b[1].priority)).forEach(e=>{
	var name = e[0]
	var data = e[1]
	var btn = f.addElement(list_box,"button",data.name)
	btn.style.width = "100px"
	btn.style.margin = "10px"
	var box = f.addElement(list_box,"div")
	box.classList.add("vertical")
	box.style.border = "2px solid white"
	box.style.margin = "10px"
	box.style.display = "none"
	btn.onclick = ()=>{box.style.display=box.style.display==="initial" ? "none" : "initial"}
	var img = f.addElement(box,"img")
	img.src = data.img
	f.addElement(box,"div",data.desc)
	f.addElement(box,"div",data.concept)
	Object.entries(data.concept_art||{}).forEach(a=>{
		var box2 = f.addElement(box,"div")
		box2.style.border="1px yellow dotted"
		box2.style.margin="5px"
		box2.style.marginLeft="80px"
		box2.classList.add("horizontal")
		var img = f.addElement(box2,"img")
		img.src = a[0]
		img.style.maxWidth = "200px"
		img.style.maxHeight = "200px"
		var desc = f.addElement(box2,"div",a[1])
		console.log(a[0],a[1])
	})
	console.log(name,data)
})