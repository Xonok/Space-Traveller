/*
CODE STATUS - outdated and mixed
*Config functions need to be moved from func to config.
*All the table stuff should be in a separate table module, like the one nav uses.
However, the functions here are still being used in Trade, so they can't be removed yet.
*Config shouldn't be in this file.
*Config in general should be moved into a separate folder.
*/

//This check is only needed because utils.load can cause .js files to be loaded twice.
if(typeof func === "undefined"){
	Object.getPrototypeOf([]).last = function(){return this[this.length-1]}
	var config = {
		generated: false,
		styles: new CSSStyleSheet(),
		apply(){
			var family = localStorage.getItem("settings:font")
			if(!family){
				family = "Arial"
			}
			config.styles.replace("*{font-family:"+family+"}")
			document.adoptedStyleSheets = [config.styles]
			config.rainbow = localStorage.getItem("settings:rainbow_mode")
			config.serious_margin = localStorage.getItem("settings:serious_margin")
		}
	}
	if(!config.generated){
		config.apply()
		config.generated = true
	}
	func = {
		init(){
			func.init_toggles()
			func.init_categories()
		},
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
			var txt = idata.name+"<br><br>"+(idata.desc || "No description available")
			idata.prop_info?.forEach(i=>{
				txt += "<br>"+"&nbsp;".repeat(4)
				txt += i.value !== undefined ? i.key+": "+i.value : i.key
			})
			var tt = f.addElement(parent,"span",func.formatString(txt))
			tt.className = "tooltiptext"
			return tt
		},
		formatString(s){
			return s ? s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;") : s
		},
		shipName(s,format){
			if(format==="character"){return s.custom_name ? s.custom_name+" #"+s.id : s.type+" #"+s.id}
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
			if(!el){throw new Error("HTML element for table doesn't exist.")}
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
				this.classes = {}
				this.buttons = {}
				this.inputs = {}
				this.max_chars2 = {}
				this.max_chars_replace = {}
				this.formatters = {}
				this.forcols = {}
				this.sort_enabled = false
			},
			update(table,draw=true){
				this.data = table
				draw && this.draw()
			},
			add_tooltip(name){
				this.tooltips[name] = true
			},
			add_class(col,name){
				if(!this.classes[col]){
					this.classes[col] = []
				}
				this.classes[col].push(name)
			},
			max_chars(col,chars,replacement="..."){
				this.max_chars2[col] = chars === -1 ? this.max_chars2[col] : chars
				this.max_chars_replace[col] = replacement
			},
			add_onclick(header,code){},
			add_button(header,txt,vis,code){
				this.buttons[header] = {
					txt,
					vis,
					code
				}
			},
			add_input(header,type,code){
				this.inputs[header] = {
					type,
					code
				}
			},
			get_input_values(header){
				console.log(this.inputs)
				var output = {}
				this.inputs[header].fields.forEach(f=>{
					if(this.inputs[header].type === "number"){
						output[f.name] = Number(f.value)
						return
					}
					output[f.name] = f.value
				})
				return output
			},
			format(header,func){
				this.formatters[header] = func
			},
			sort(){
				this.sort_enabled = true
			},
			for_col(header,func){
				this.forcols[header] = func
			},
			draw(){
				var el = this.el
				el.innerHTML = ""
				var headers = this.headers.map(h=>h.display)
				func.headers(el,...headers)
				var rows = 0
				var keys = this.sort_enabled ? Object.keys(this.data).sort() : Object.keys(this.data)
				Object.values(this.inputs).forEach(e=>e.fields = [])
				keys.forEach(name=>{
					var data = []
					var buttons = []
					var inputs = []
					this.headers.forEach(h=>{
						var key = h.key
						var val = this.data[name][key]
						if(this.formatters[key]){
							val = this.formatters[key](this.data[name])
						}
						if(val === undefined){
							val = ""
						}
						if(this.max_chars2[key]){
							var len = val.length
							var diff = len - this.max_chars2[key]
							if(diff > 0){
								val = val.slice(0,-diff)+this.max_chars_replace[key]
							}
						}
						if(config.rainbow && this.data[name][key+"_pluto"]){
							val = this.data[name][key+"_pluto"]
						}
						var div = document.createElement("td")
						var original_div = div
						div.innerHTML = val
						var img
						if(typeof val === "string" && val.startsWith("img/")){
							div.innerHTML = ""
							div.classList.add("centered_")
							img = func.addElement(div,"img")
							img.src = val
						}
						var btn = this.buttons[key]
						if(btn){
							var hide = Object.entries(btn.vis||[]).find(v=>{
								var cond = v[0]
								var val = v[1]
								return this.data[name][cond] !== val
							})
							if(!hide){
								var btn_el = document.createElement("button")
								btn_el.innerHTML = btn.txt || val
								btn_el.code = btn.code
								div = btn_el
								buttons.push(btn_el)
							}
						}
						var input = this.inputs[key]
						if(input){
							var input_el = document.createElement("input")
							input_el.code = input.code
							input_el.name = name
							div = input_el
							inputs.push(input_el)
							this.inputs[key].fields.push(input_el)
						}
						var tooltip = this.tooltips[key]
						if(tooltip){
							div.classList.add("item_name")
							func.tooltip(div,this.data[name])
						}
						var classes = this.classes[key]
						if(classes){
							classes.forEach(c=>{
								div.classList.add(c)
								if(img){img.classList.add(c)}
							})
						}
						div.key = key
						data.push(div)
					})
					var r = func.row(el,...data)
					r.name = name
					buttons.forEach(b=>b.onclick=()=>b.code(r))
					inputs.forEach(i=>i.oninput=()=>i.code(r))
					data.forEach(d=>{
						var key = d.key
						if(this.forcols[key]){
							val = this.forcols[key](d,this.data[name])
						}
					})
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
		},
		init_toggles(){
			func.forClass("btn_toggle",e=>{
				var [name_closed,name_open] = e.innerHTML.split("/")
				var name_open="<button>"+name_open+"/</button>"
				var toggle_status = false
				e.innerHTML = name_closed
				func.forClass(e.getAttribute("toggle"),e=>{
					e.style.display = "none"
				})
				e.onclick = ()=>{
					toggle_status = !toggle_status
					e.innerHTML = toggle_status ? name_open : name_closed
					func.forClass(e.getAttribute("toggle"),e=>{
						e.style.display = toggle_status ? null : "none"
					})	
				}
				//console.log(e,e.getAttribute("toggle"),e.innerHTML) //Split with / to get button names
			})
		},
		init_categories(){
			var categories = {}
			func.forClass("btn_category",e=>{
				var cat = e.getAttribute("category_name")
				var tar = e.getAttribute("category_target")
				if(!categories[cat]){
					categories[cat]={
						"buttons": [],
						"targets": []
					}
				}
				categories[cat].buttons.push(e)
				categories[cat].targets.push(tar)
				e.onclick = e2=>{
					categories[cat].targets.forEach(t=>{
						window[t].style.display = "none"
					})
					categories[cat].buttons.forEach(b=>{
						b.classList.remove(cat+"_active")
					})
					e.classList.add(cat+"_active")
					window[tar].style.display = null
				}
			})
			func.forClass("category",e=>{
				e.style.display = "none"
			})
			Object.entries(categories).forEach(e=>{
				var name = e[0]
				var data = e[1]
				data.buttons[0].click()
			})
		},
	}
}

