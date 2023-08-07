/*
CODE STATUS - outdated and mixed
*Config functions need to be moved from func to config.
*All the table stuff should be in a separate table module, like the one nav uses.
However, the functions here are still being used in Trade, so they can't be removed yet.
*Config shouldn't be in this file.
*Config in general should be moved into a separate folder.
*/

Object.getPrototypeOf([]).last = function(){return this[this.length-1]}
var config = {
	styles: document.styleSheets[0],
	apply(){
		var family = localStorage.getItem("settings:font")
		if(!family){
			family = "Arial"
		}
		config.styles.insertRule("*{font-family:"+family+"}")
		config.rainbow = localStorage.getItem("settings:rainbow_mode")
		config.serious_margin = localStorage.getItem("settings:serious_margin")
	}
}
config.apply()
func = {
	getSetting(name){
		return localStorage.getItem("settings:"+name)
	},
	setSetting(name,value){
		if(value === null || value === undefined){
			localStorage.removeItem("settings:"+name)
		}
		else{
			localStorage.setItem("settings:"+name,value)
		}
	},
	formatNumber(number){
		var locale = func.getSetting("locale") || undefined
		return number.toLocaleString(locale)
	},
	addElement(parent,type,inner,before=false){
		var e = document.createElement(type)
		if(inner!==undefined){e.innerHTML=inner}
		before ? parent.prepend(e) : parent.append(e)
		return e
	},
	headers(parent,...names){
		var row = f.addElement(parent,"tr")
		row.type = "headers"
		names.forEach(n=>f.addElement(row,"th",n))
	},
	row(parent,...data){
		var r = f.addElement(parent,"tr")
		data.forEach(d=>{
			if(typeof d === "number"){
				var el = f.addElement(r,"td",d)
				el.classList.add("align_center")
			}
			else if(typeof d === "string"){
				f.addElement(r,"td",d)
			}
			else if(d.tagName === "TD"){
				r.append(d)
			}
			else if(d instanceof Element){
				f.addElement(r,"td").append(d)
			}
			else{
				console.log(d)
				throw new Error("Unknown element type for row.")
			}
		})
		return r
	},
	tooltip(parent,idata){
		var txt = idata.desc
		idata.prop_info?.forEach(i=>{
			txt += "<br>"+"&nbsp;".repeat(4)
			txt += i.value ? i.key+": "+i.value : i.key
		})
		var tt = f.addElement(parent,"span",func.formatString(txt))
		tt.className = "tooltiptext"
		return tt
	},
	formatString(s){
		return s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;")
	},
	shipName(s,format){
		if(format==="character"){return s.custom_name || s.type+" #"+s.id}
		if(format==="test"){return s.custom_name ||"#"+s.id}
		if(format==="stranger"){return s.owner+" #"+s.id}
	},
	forClass(name,func){
		Array.from(document.getElementsByClassName(name)).forEach(func)
	},
	input(value,func){
		var e = document.createElement("input")
		if(value!=undefined && value != null){e.value = value}
		if(func){e.oninput = func}
		return e
	},
	only_numbers(e){
		var el = e.target
		if(el.value === ""){return}
		var val = Number(el.value)
		if(isNaN(val) || !Number.isInteger(val)){
			el.value = el.saved_value
		}
		else if(val===0){
			el.value = ""
		}
		else{
			el.saved_value = val
			el.value = val
		}
	},
	make_table(el,...headers){
		var t = Object.create(func.table)
		t.el = el
		t.headers = []
		headers.forEach(h=>{
			var key = h
			var display = h
			if(typeof h === "object"){
				key = Object.keys(h)[0]
				display = h[key]
			}
			var entry = {
				key: key,
				display: display
			}
			t.headers.push(entry)
		})
		t.init()
		return t
	},
	table: {
		//Don't use this directly. Always use make_table.
		init(){
			this.tooltips = {}
			this.buttons = {}
		},
		update(table,draw=true){
			this.data = table
			draw && this.draw()
		},
		add_tooltip(name){
			this.tooltips[name] = true
		},
		add_onclick(header,code){},
		add_button(header,txt,vis,code){
			this.buttons[header] = {
				txt: txt,
				vis: vis,
				code: code
			}
		},
		draw(){
			var el = this.el
			el.innerHTML = ""
			var headers = this.headers.map(h=>h.display)
			func.headers(el,...headers)
			var rows = 0
			Object.entries(this.data).forEach(e=>{
				var name = e[0]
				var data = []
				var buttons = []
				this.headers.forEach(h=>{
					var key = h.key
					var val = this.data[name][key]
					if(val === undefined){
						val = ""
					}
					if(config.rainbow && this.data[name][key+"_pluto"]){
						val = this.data[name][key+"_pluto"]
					}
					if(typeof val === "string" && val.startsWith("img/")){
						var img_box = document.createElement("td")
						img_box.classList.add("centered_")
						var img = func.addElement(img_box,"img")
						img.src = val
						val = img_box
					}
					var btn = this.buttons[key]
					if(btn){
						var hide = Object.entries(btn.vis).find(v=>{
							var cond = v[0]
							var val = v[1]
							return this.data[name][cond] !== val
						})
						if(!hide){
							var btn_el = document.createElement("button")
							btn_el.innerHTML = btn.txt
							btn_el.code = btn.code
							val = btn_el
							buttons.push(btn_el)
						}
					}
					var tooltip = this.tooltips[key]
					if(tooltip){
						var div = document.createElement("td")
						div.innerHTML = val
						div.classList.add("item_name")
						func.tooltip(div,this.data[name])
						val = div
					}
					data.push(val)
				})
				var r = func.row(el,...data)
				r.name = name
				buttons.forEach(b=>b.onclick=()=>b.code(r))
				rows++
			})
			if(!rows){
				el.innerHTML = ""
			}
		}
	},
	join_inv(amounts,idata){
		var result = {}
		Object.entries(amounts).forEach(e=>{
			var key = e[0]
			var amount = e[1]
			var entry = Object.assign({},idata[key])
			entry.amount = amount
			result[key] = entry
		})
		return result
	},
	load(obj,path,key){
		switch(key){
			case "folders":
				Object.keys(obj).forEach(k=>{
					func.load(obj[k],path+k+"\\",k)
				})
				break
			case "files":
				obj.forEach(f=>{
					var script = document.createElement("script")
					script.src = path+f+".js"
					script.async = false
					document.body.appendChild(script)
					//console.log("Filepath: "+path+f+".js")
				})
				break
			default:
				Object.keys(obj).forEach(k=>{
					func.load(obj[k],path,k)
				})
				break
		}
	}
}