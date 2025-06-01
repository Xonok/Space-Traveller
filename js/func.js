/*
CODE STATUS - outdated and mixed
*Config functions need to be moved from func to config.
*All the table stuff should be in a separate table module, like the one nav uses.
However, the functions here are still being used in Trade, so they can't be removed yet.
*Config shouldn't be in this file.
*Config in general should be moved into a separate folder.
*/

Object.getPrototypeOf([]).last = function(){return this[this.length-1]}
Object.getPrototypeOf({}).forEach = function(c){Object.entries(this).forEach(e=>c(e[0],e[1]))}
Object.getPrototypeOf({}).map = function(c){return Object.fromEntries(Object.entries(this).map(e=>[e[0],c(e[1])]))}
//This check is only needed because utils.load can cause .js files to be loaded twice.
if(typeof func === "undefined"){
	var config = {
		generated: false,
		styles: new CSSStyleSheet(),
		rules: [],
		apply(){
			var add_rule = data=>config.rules.push(config.styles.insertRule(data))
			var family = localStorage.getItem("settings:font")
			if(!family){
				family = "Arial"
			}
			document.adoptedStyleSheets = [config.styles]
			config.rainbow = localStorage.getItem("settings:rainbow_mode")
			config.serious_margin = localStorage.getItem("settings:serious_margin")
			config.grayscale = localStorage.getItem("settings:grayscale")
			
			config.rules.forEach(r=>config.styles.deleteRule(r))
			config.rules = []
			add_rule("*{font-family:"+family+"}")
			config.grayscale && add_rule("html {-moz-filter: grayscale(100%);-webkit-filter: grayscale(100%);filter: gray;filter; grayscale(100%);}")
		}
	}
	if(!config.generated){
		var ctx = {}
		config.apply()
		config.generated = true
	}
	var pagename = window.location.pathname.split("/").pop().split(".")[0]
	func = {
		init(){
			func.init_toggles()
			func.init_categories()
			func.view.init()
		},
		send(command,table={},auth=true){
			if(auth){
				var key = localStorage.getItem("key")
				table.key = key
			}
			table.command = command
			if(q.pship !== q.cdata?.ship){
				table.active_ship = q.pship.name
			}
			var char = sessionStorage.getItem("char")
			if(char && !table.active_character){
				table.active_character = char
			}
			var jmsg = JSON.stringify(table)
			var req = new XMLHttpRequest()
			req.open("POST",window.location.href,true)
			req.onload = e=>{
				if(e.target.status===200){
					f.forClass("error_display",el=>{
						el.innerHTML = ""
					})
					f.forClass("info_display",el=>{
						el.innerHTML = ""
					})
					var url = e.target.responseURL
					var loc = window.location.pathname
					if(!url.includes(loc)){
						var tokens = url.split("/")
						var view_name = tokens.last().replace(".html","")
						if(f.view.views[view_name]){
							f.view.open(view_name)
						}
						else{
							window.location.href = url
						}
						return
					}
					var msg = JSON.parse(e.target.response)
					query.receive(msg)
					if(q.cdata){
						document.title = "Space Traveller: "+q.cdata.name
					}
					var msg_txt = ""
					q.messages?.forEach((m,mID)=>{
						msg_txt += f.formatString(m)
						if(mID+1 < q.messages.length){
							msg_txt += "<br>"
						}
					})
					if(!msg_txt){
						func.prev_msg_count = 0
						func.prev_msg = undefined
					}
					else if(msg_txt === func.prev_msg){
						func.prev_msg_count++
						func.forClass("info_display",e=>{
							e.innerHTML = msg_txt+"("+func.prev_msg_count+")"
						})
					}
					else{
						func.forClass("info_display",e=>{
							e.innerHTML = msg_txt
						})
						func.prev_msg_count = 1
					}
					func.prev_msg = msg_txt
					console.log(msg)
					func.view.receive(msg)
					var local_ship = localStorage.getItem("ship")
					if(local_ship && q.pships && Object.keys(q.pships).includes(local_ship)){
						q.pship = q.pships[local_ship]
					}
				}
				else if(e.target.status===400){
					f.forClass("error_display",el=>{
						el.innerHTML = e.target.response
					})
					console.log(e.target.response)
				}
				else if(e.target.status===500){
					f.forClass("error_display",el=>{
						el.innerHTML = "Server error."
					})
					console.log(e.target.response)
				}
				else{
					throw new Error("Unknown response status "+e.target.status)
				}
			}
			req.send(jmsg)
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
			var locale = func.getSetting("locale") || navigator.languages
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
			return row
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
		item_txt(idata){
			var txt = idata.name+"<br><br>"+(idata.desc || "No description available")
			idata.prop_info?.forEach(i=>{
				txt += "<br>"+"&nbsp;".repeat(4)
				txt += i.value !== undefined ? i.key+": "+i.value : i.key
			})
			txt = func.formatString(txt)
			return txt
		},
		tooltip(parent,idata){
			parent.classList.add("tt_parent","dotted")
			var txt = func.item_txt(idata)
			var tt = f.addElement(parent,"span",txt)
			tt.className = "tooltiptext"
			return tt
		},
		tooltip2(parent,txt){
			parent.classList.add("tt_parent","dotted")
			var tt = f.addElement(parent,"div")
			tt.className = "tooltiptext"
			if(Array.isArray(txt)){
				txt.forEach(t=>{
					tt.append(t)
				})
			}
			else{
				tt.innerHTML = func.formatString(txt)
			}
			
			return tt
		},
		item_tooltip(parent,idata){
			var box = document.createElement("div")
			box.classList.add("horizontal")
			var img_box = f.img_box(box,"50px","50px",idata.img)
			img_box.style.marginTop = "2rem"
			img_box.style.marginRight = "5px"
			f.addElement(box,"div",f.item_txt(idata))
			return func.tooltip2(parent,[box])
		},
		formatString(s){
			return s ? s.replaceAll("\n","<br>").replaceAll("\t","&nbsp;&nbsp;&nbsp;&nbsp;") : s
		},
		shipName(s,format){
			if(format==="character"){return s.custom_name ? s.custom_name+" #"+s.id : s.type+" #"+s.id}
			if(format==="test"){return s.custom_name ||"#"+s.id}
			if(format==="station"){return s.custom_name || s.name}
			if(format==="stranger"){
				if(s.custom_name){
					return s.custom_name
				}
				if(!s.id){
					return s.name
				}
				return s.owner+" #"+s.id
			}
		},
		forClass(name,func){
			Array.from(document.getElementsByClassName(name)).forEach(func)
		},
		input(value,func){
			var e = document.createElement("input")
			if(value!== undefined && value !== null){
				e.value = value
				e.saved_value = value
			}
			if(func){e.oninput = func}
			return e
		},
		img_box(parent,width,height,src){
			var box = f.addElement(parent,"div")
			box.style.width = width
			box.style.height = height
			box.classList.add("centered")
			var img = f.addElement(box,"img")
			img.src = src
			img.style.maxWidth = width
			img.style.maxHeight = height
			return box
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
		squirrel_2d(indexX,indexY,seed){
			var PRIME_NUMBER = 198491317 // Large prime number with non-boring bits
			return f.squirrel_5(indexX + (PRIME_NUMBER * indexY), seed)
		},
		squirrel_2d_unit(indexX,indexY,seed){
			const ONE_OVER_MAX_UINT = 1.0 / 0xFFFFFFFF // Precomputed constant
			return ONE_OVER_MAX_UINT * f.squirrel_2d(indexX, indexY, seed)
		},
		squirrel_5(positionX,seed){
			var SQ5_BIT_NOISE1 = 0xd2a80a3f // 11010010101010000000101000111111
			var SQ5_BIT_NOISE2 = 0xa884f197 // 10101000100001001111000110010111
			var SQ5_BIT_NOISE3 = 0x6C736F4B // 01101100011100110110111101001011
			var SQ5_BIT_NOISE4 = 0xB79F3ABB // 10110111100111110011101010111011
			var SQ5_BIT_NOISE5 = 0x1b56c4f5 // 00011011010101101100010011110101

			var mangledBits = positionX >>> 0 // Ensure unsigned integer
			mangledBits *= SQ5_BIT_NOISE1
			mangledBits += seed
			mangledBits ^= (mangledBits >>> 9)
			mangledBits += SQ5_BIT_NOISE2
			mangledBits ^= (mangledBits >>> 11)
			mangledBits *= SQ5_BIT_NOISE3
			mangledBits ^= (mangledBits >>> 13)
			mangledBits += SQ5_BIT_NOISE4
			mangledBits ^= (mangledBits >>> 15)
			mangledBits *= SQ5_BIT_NOISE5
			mangledBits ^= (mangledBits >>> 17)

			return mangledBits >>> 0 // Ensure unsigned integer
		},
		next_tick(tick_type){
			time_per_tick = {
				"short": 60*5, // 5 minutes
				"long": 60*60*3, // 3 hours
				"day": 60*60*24 // 24 hours
			}
			var now = Date.now()/1000
			var then = Math.ceil(now/time_per_tick[tick_type])*time_per_tick[tick_type]
			return then-now
		},
		itype(item){
			if(q.idata[item]){
				if(q.idata[item].type){
					return q.idata[item]["type"]
				}	
				return "other"
			}
				
			if(q.ship_types[item]){
				return "ship"
			}
			console.log("Unknown kind of item: "+item)
		},
		str_to_int(str){
			var hash = 0
			for (let i = 0; i < str.length; i++) {
				var char = str.charCodeAt(i) // Get ASCII code of character
				hash = (hash * 31 + char) | 0  // Multiply by a prime number and add char code
			}
			return hash >>> 0 // Ensure the hash is unsigned (32-bit positive integer)
		},
		make_table(el,...headers){
			var t = Object.create(func.table)
			if(!el){throw new Error("HTML element for table doesn't exist.")}
			t.el = el
			t.headers = []
			headers.forEach(h=>{
				var key = h
				var display = h
				var alt
				if(typeof h === "object"){
					key = Object.keys(h)[0]
					display = h[key]
					alt = h.alt
				}
				var entry = {
					key,
					display,
					alt
				}
				t.headers.push(entry)
			})
			t.init()
			el.table = t
			return t
		},
		table: {
			//Don't use this directly. Always use make_table.
			init(){
				this.header_types = {}
				this.tooltips = {}
				this.tooltips2 = {}
				this.item_tooltips = {}
				this.classes = {}
				this.onclicks = {}
				this.buttons = {}
				this.inputs = {}
				this.dropdowns = {}
				this.cells = {}
				this.max_chars2 = {}
				this.max_chars_replace = {}
				this.formatters = {}
				this.forcols = {}
				this.sort_order = []
				this.rows = {}
			},
			update(table,draw=true){
				this.data = table
				draw && this.draw()
			},
			set_header_types(header_types){
				this.header_types = header_types
			},
			force_headers(state){
				this.force = state
			},
			sticky_headers(state){
				this.sticky_headers_on = state
			},
			hide_headers(state){
				this.hide_headers = state
			},
			add_tooltip(name){
				this.tooltips[name] = true
			},
			add_tooltip2(name,code){
				this.tooltips2[name] = code
			},
			add_item_tooltip(name){
				this.item_tooltips[name] = true
			},
			add_class(col,...names){
				if(!this.classes[col]){
					this.classes[col] = []
				}
				names.forEach(n=>{
					this.classes[col].push(n)
				})
			},
			max_chars(col,chars,replacement="..."){
				this.max_chars2[col] = chars === -1 ? this.max_chars2[col] : chars
				this.max_chars_replace[col] = replacement
			},
			add_onclick(header,code){
				this.onclicks[header] = {
					code
				}
			},
			add_button(header,txt,vis,code){
				this.buttons[header] = {
					txt,
					vis,
					code
				}
			},
			add_input(header,type,code,placeholder){
				this.inputs[header] = {
					type,
					code,
					placeholder
				}
			},
			add_dropdown(header,options,groups,def_value){
				this.dropdowns[header] = {
					"options": options || [],
					"groups": groups || {},
					"def_value": def_value
				}
			},
			get_input_values(header){
				var output = {}
				this.inputs[header].fields.forEach(f=>{
					var type = this.inputs[header].type
					val = f.value
					switch(type){
						case "number":
							val = Number(f.value) || 0
							break
						case "int+":
							val = Math.floor(Math.max(0,val)) || 0
							break
						case "int":
							val = Math.floor(val) || 0
							break
					}
					if(val){
						output[f.name] = val
					}
				})
				return output
			},
			get_values(header,type){
				var output = {}
				this.cells[header].forEach(c=>{
					output[c.name] = type(c.value || c.innerHTML)
				})
				return output
			},
			format(header,func){
				this.formatters[header] = func
			},
			sort(...order){
				this.sort_order = order
			},
			for_col(header,func){
				this.forcols[header] = func
			},
			_get_val(td){
				var child_val = td.childNodes[0]?.value
				var val = child_val === undefined ? td.innerHTML : child_val
				var desired_type = this.header_types[td.key]
				if(desired_type){
					switch(desired_type){
						case "int":
							val = Math.floor(Number(val))
							//no breka
						case "int+":
							val = Math.max(0,val)
							break
						default:
							throw new Error("Unknown desired type: "+desired_type)
					}
				} 
				return val
			},
			get_data(){
				var output = {}
				Object.entries(this.rows).forEach(r=>{
					var key = r[0]
					var value = r[1]
					var data = Array.from(value.childNodes).map(td=>{
						return [td.key,this._get_val(td)]
					})
					output[key] = Object.fromEntries(data)
				})
				return output
			},
			draw(){
				var el = this.el
				el.innerHTML = ""
				var id = el.id
				var headers = this.headers.map(h=>h.display)
				if(this.hide_headers !== true){
					var h_row = func.headers(el,...headers)
					if(this.sticky_headers_on){
						h_row.style.position = "sticky"
						h_row.style.top = "0"
						h_row.style.zIndex = "5"
					}
				}
				this.rows = {}
				this.cells = {}
				this.headers.forEach(h=>{
					var key = h.key
					this.cells[key] = []
				})
				var rows = 0
				var keys = Object.keys(this.data)
				this.sort_order.forEach(so=>{
					mult = 1
					if(so.charAt(0)==="!"){
						so = so.slice(1)
						mult = -1
					}
					keys.sort((a,b)=>{
						var a_data = this.data[a][so]
						var b_data = this.data[b][so]
						if(a_data === undefined){
							a_data = Number.MIN_VALUE
						}
						if(b_data === undefined){
							b_data = Number.MIN_VALUE
						}
						if(a_data === b_data){
							return 0
						}
						else if(a_data > b_data){
							return 1*mult
						}
						else if(a_data < b_data){
							return -1*mult
						}
					})
				})
				Object.values(this.inputs).forEach(e=>e.fields = [])
				keys.forEach(name=>{
					var data = []
					var divs = []
					var onclicks = []
					var buttons = []
					var inputs = []
					var fields = {}
					this.headers.forEach(h=>{
						var key = h.key
						var alt = h.alt
						var val = this.data[name][alt] || this.data[name][key]
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
						var td = div
						var col_class = "table__"+key
						var table_col_class = id+"__"+key
						div.classList.add(col_class,table_col_class)
						var img
						if(typeof val === "string" && val.startsWith("img/")){
							div.innerHTML = ""
							div.classList.add("centered_")
							img = func.addElement(td,"img")
							img.src = val
							div = img
						}
						var btn = this.buttons[key]
						if(btn){
							var hide = Object.entries(btn.vis||[]).find(v=>{
								var cond = v[0]
								var val = v[1]
								return this.data[name][cond] !== val
							})
							if(!hide){
								var btn_el = func.addElement(td,"button")
								btn_el.innerHTML = btn.txt || val
								btn_el.code = btn.code
								div = btn_el
								buttons.push(btn_el)
							}
						}
						var input = this.inputs[key]
						if(input){
							var input_el = func.addElement(td,"input")
							input_el.code = input.code
							input_el.name = name
							input_el.saved_value = ""
							if(input.placeholder !== undefined){
								input_el.placeholder = 0
								input_el.onfocus = ()=>{input_el.placeholder=""}
								input_el.onblur = ()=>{input_el.placeholder=input.placeholder}
							}
							input_el.value = val
							div = input_el
							if(input.code){
								inputs.push(input_el)
								
							}
							this.inputs[key].fields.push(input_el)
						}
						var dropdown = this.dropdowns[key]
						if(dropdown){
							var select = func.addElement(td,"select")
							if(dropdown.def_value){
								var opt = func.addElement(select,"option")
								opt.value = ""
								opt.innerHTML = dropdown.def_value
							}
							dropdown.options.forEach(o=>{
								var opt = func.addElement(select,"option")
								opt.value = typeof(o) === "string" ? o : o[0]
								opt.innerHTML = typeof(o) === "string" ? o : o[1]
							})
							Object.entries(dropdown.groups).forEach(e=>{
								var key = e[0]
								var val = e[1]
								var ogroup = func.addElement(select,"optgroup")
								ogroup.label = key
								val.forEach(v=>{
									var opt = func.addElement(ogroup,"option")
									opt.value = typeof(v) === "string" ? v : v[0]
									opt.innerHTML = typeof(v) === "string" ? v : v[1]
								})
							})
							select.value = val
							if(!val){
								select.value = ""
							}
							div = select
						}
						if(td === div){
							div.innerHTML = val
						}
						var tooltip = this.tooltips[key]
						if(tooltip){
							div.classList.add("item_name")
							func.tooltip(div,this.data[name])
						}
						var tooltip2 = this.tooltips2[key]
						if(tooltip2){
							div.classList.add("item_name")
							func.tooltip2(div,tooltip2(this.data[name]))
						}
						var item_tooltip = this.item_tooltips[key]
						if(item_tooltip){
							div.classList.add("item_name")
							func.item_tooltip(div,this.data[name])
						}
						var onclick = this.onclicks[key]
						if(onclick){
							onclicks.push([div,onclick.code])
						}
						var classes = this.classes[key]
						if(classes){
							classes.forEach(c=>{
								div.classList.add(c)
								if(img){img.classList.add(c)}
							})
						}
						td.key = key
						td.name = name
						div.key = key
						div.name = name
						data.push(td)
						divs.push(div)
						fields[key] = div
						this.cells[key].push(div)
					})
					var r = func.row(el,...data)
					r.name = name
					r.field = fields
					buttons.forEach(b=>b.onclick=()=>b.code(r))
					inputs.forEach(i=>i.oninput=e=>i.code(e,r))
					onclicks.forEach(o=>o[0].onclick=()=>o[1](r))
					divs.forEach(d=>{
						var key = d.key
						if(this.forcols[key]){
							val = this.forcols[key](d,this.data[name],name)
						}
					})
					this.rows[name] = r
					rows++
				})
				if(!rows && !this.force){
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
				var [name_closed,name_open] = e.innerHTML.split("//")
				var default_state = e.getAttribute("default") || "closed"
				var toggle_status = default_state === "open"
				e.innerHTML = toggle_status ? name_open : name_closed
				func.forClass(e.getAttribute("toggle"),e=>{
					e.style.display = default_state === "open" ? "initial" : "none"
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
						b.classList.remove("category_active")
					})
					e.classList.add(cat+"_active")
					e.classList.add("category_active")
					window[tar].style.display = null
					localStorage.setItem(pagename+","+cat+":target",tar)
				}
			})
			func.forClass("category",e=>{
				e.style.display = "none"
			})
			Object.entries(categories).forEach(e=>{
				var name = e[0]
				var data = e[1]
				var target = localStorage.getItem(pagename+","+name+":target")
				data.buttons.forEach((b,idx)=>{
					var tar = b.getAttribute("category_target")
					var do_click = target ? tar===target : !idx
					do_click && b.click()
				})
			})
		},
		dict_removes(table,...args){
			args.forEach(a=>delete table[a])
			return table
		},
		dict_mult(a,b){
			var result = {}
			Object.entries(a).forEach(e=>result[e[0]] = e[1]*b[e[0]])
			return result
		},
		dict_mult2(a,n){
			var result = {}
			Object.entries(a).forEach(e=>result[e[0]] = e[1]*n)
			return result
		},
		dict_sum(table){
			return Object.values(table).reduce((a,b)=>a+b,0)
		},
		dict_add(table,...args){
			args.forEach(a=>{
				Object.entries(a).forEach(e=>{
					var key = e[0]
					var val = e[1]
					if(!table[key]){
						table[key] = 0
					}
					table[key] += val
				})
			})
			return table
		},
		dict_merge(table,...args){
			args.forEach(a=>{
				Object.entries(a).forEach(e=>{
					var key = e[0]
					var val = e[1]
					table[key] = val
				})
			})
			return table
		}
	}
	var f = func
}

