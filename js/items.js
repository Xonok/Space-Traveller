/*
CODE STATUS - experimental
This code doesn't do anything we really want. It only exists to test stuff.
*/

var f = func
const key = localStorage.getItem("key")
if(!key){
	window.location.href = "/login.html"
	throw new Error("Not logged in.")
}

//window.button_name.onclick = do_button_name

function send(command,table={}){
	table.key = key
	table.command = command 
	var jmsg = JSON.stringify(table)
	var req = new XMLHttpRequest()
	req.open("POST",window.location.href,true)
	req.onload = e=>{
		if(e.target.status===200){
			window.error_display.innerHTML = ""
			var url = e.target.responseURL
			var loc = window.location.pathname
			if(!url.includes(loc)){
				window.location.href = url+window.location.search
				return
			}
			var msg = JSON.parse(e.target.response)
			console.log(msg)
		}
		else if(e.target.status===400){
			window.error_display.innerHTML = e.target.response
			console.log(e.target.response)
		}
		else if(e.target.status===500){
			window.error_display.innerHTML = "Server error."
			console.log(e.target.response)
		}
		else{
			throw new Error("Unknown response status "+e.target.status)
		}
	}
	req.send(jmsg)
}
function forClass(name,func){
	Array.from(document.getElementsByClassName(name)).forEach(func)
}
function table(parent,headers){
	var t = f.addElement(parent,"table")
	t.data = []
	t.headers = headers
	var header_row = f.addElement(t,"tr")
	headers.forEach(h=>f.addElement(header_row,"th",h.name))
	var add_row = f.addElement(t,"tr")
	var add_button_box = f.addElement(add_row,"td")
	add_button_box.colSpan = "5"
	var add_button = f.addElement(add_button_box,"button","Add...")
	add_button.style.width = "100%"
	add_button.onclick = ()=>{
		var row = document.createElement("tr")
		t.insertBefore(row,add_row)
		var edata = {}
		row.edata = edata
		t.data.push(edata)
		headers.forEach(h=>{
			var {name,initial} = h
			var e = f.addElement(row,"td",initial)
			edata[name.toLowerCase()] = initial
			e.contentEditable = "true"
			e.fieldname = name.toLowerCase()
			e.onblur = ()=>{
				edata[e.fieldname] = e.innerText
				console.log(e.innerText,edata)
			}
		})
	}
	return t
}

var headers = [
	{
		"name": "Name",
		"initial": "blah"
	},
	{
		"name": "Price",
		"initial": "0"
	},
	{
		"name": "Size",
		"initial": "1"
	},
	{
		"name": "Type",
		"initial": "misc"
	},
	{
		"name": "Note",
		"initial": ""
	}
]
function update_table(table,data){
	var rows = Array.from(table.childNodes)
	rows.shift()
	var last = rows.pop()
	var header_names = table.headers.map(h=>h.name.toLowerCase())
	rows.forEach(r=>{
		table.remove(r)
	})
}
// var parent=document.getElementsByClassName("tabcontent")
var items
function add_content(parent){
	var items = table(parent,headers)
	update_table(items)
	var save_btn = f.addElement(parent,"button","Save")
	save_btn.style.margin="5px"
}
f.forClass("tabcontent",add_content)

send("userdata-get")
