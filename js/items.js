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
function addElement(parent,type,inner){
	var e = document.createElement(type)
	if(inner!==undefined){e.innerHTML=inner}
	parent.append(e)
	return e
}
function forClass(name,func){
	Array.from(document.getElementsByClassName(name)).forEach(func)
}
function table(parent,headers){
	var t = addElement(parent,"table")
	t.data = []
	t.headers = headers
	var header_row = addElement(t,"tr")
	headers.forEach(h=>addElement(header_row,"th",h.name))
	var add_row = addElement(t,"tr")
	var add_button_box = addElement(add_row,"td")
	add_button_box.colSpan = "5"
	var add_button = addElement(add_button_box,"button","Add...")
	add_button.style.width = "100%"
	add_button.onclick = ()=>{
		var row = document.createElement("tr")
		t.insertBefore(row,add_row)
		var edata = {}
		row.edata = edata
		t.data.push(edata)
		headers.forEach(h=>{
			var {name,initial} = h
			var e = addElement(row,"td",initial)
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
var save_btn = addElement(document.body,"button","Save")
var items = table(document.body,headers)
update_table(items)

send("userdata-get")
