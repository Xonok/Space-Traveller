var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

var list_box = window.buttons
Object.entries(art.entries).sort((a,b)=>{
	if(a[1].priority>b[1].priority){
		return -1
	}
	else if(a[1].priority<b[1].priority){
		return 1
	}
}).forEach(e=>{
	var name = e[0]
	var data = e[1]
	var btn = f.addElement(list_box,"button",data.name)
	btn.style.width = "100px"
	btn.style.margin = "10px"
	var box = f.addElement(list_box,"div")
	box.classList.add("vertical")
	box.style.border = "2px solid rgb(0, 191, 255)"
	box.style.margin = "10px"
	box.style.display = "none"
	btn.onclick = ()=>{box.style.display=box.style.display==="initial" ? "none" : "initial"}
	var img_box=f.addElement(box,"div")
	img_box.classList.add("horizontal")
	img_box.style.border="1px solid rgb(0, 191, 255)"
	var img_box2=f.addElement(img_box,"div")
	img_box2.style.borderRight="2px solid rgb(0, 191, 255)"
	img_box2.style.padding="10px"
	if(data.img){
		var img = f.addElement(img_box2,"img")
		img.src = data.img
		img.style.maxHeight="200px"
		img.style.minHeight="80px"
		img.style.maxWidth="200px"
		img.style.minWidth="80px"
		img.style.marginLeft="20px"
		img.style.marginRight="20px"
	}
	var text_box=f.addElement(img_box,"div")
	text_box.classList.add("vertical")
	text_box.style.padding="5px"
	var desc=f.addElement(text_box,"div",data.desc)
	desc.style.color="lightyellow"
	var concept=f.addElement(text_box,"div",data.concept)
	concept.style.color="lightblue"
	Object.entries(data.concept_art||{}).forEach(a=>{
		var box2 = f.addElement(box,"div")
		box2.style.border="1px rgb(0, 191, 255) dotted"
		box2.style.padding="5px"
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