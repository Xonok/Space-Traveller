var table = {
	make(el,...headers){
		var t = Object.create(table._table)
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
	_table: {
		//Don't use this directly. Always use make_table.
		init(){
			this.header_types = {}
			this.tooltips = {}
			this.tooltips2 = {}
			this.tooltips3 = {}
			this.item_tooltips = {}
			this.classes = {}
			this.onclicks = {}
			this.buttons = {}
			this.inputs = {}
			this.dropdowns = {}
			this.grades = []
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
		add_tooltip3(name,code){
			this.tooltips3[name] = code
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
		show_grade(...headers){
			this.grades = headers
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
						//no break
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
				var h_row = html.headers(el,...headers)
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
						img = html.addElement(td,"img")
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
							var btn_el = html.addElement(td,"button")
							btn_el.innerHTML = btn.txt || val
							btn_el.code = btn.code
							div = btn_el
							buttons.push(btn_el)
						}
					}
					var input = this.inputs[key]
					if(input){
						var input_el = html.addElement(td,"input")
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
						var select = html.addElement(td,"select")
						if(dropdown.def_value){
							var opt = html.addElement(select,"option")
							opt.value = ""
							opt.innerHTML = dropdown.def_value
						}
						dropdown.options.forEach(o=>{
							var opt = html.addElement(select,"option")
							opt.value = typeof(o) === "string" ? o : o[0]
							opt.innerHTML = typeof(o) === "string" ? o : o[1]
						})
						Object.entries(dropdown.groups).forEach(e=>{
							var key = e[0]
							var val = e[1]
							var ogroup = html.addElement(select,"optgroup")
							ogroup.label = key
							val.forEach(v=>{
								var opt = html.addElement(ogroup,"option")
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
					var tooltip3 = this.tooltips3[key]
					if(tooltip3){
						div.classList.add("item_name")
						func.tooltip3(div,tooltip3(this.data[name]))
					}
					var item_tooltip = this.item_tooltips[key]
					if(item_tooltip){
						div.classList.add("item_name")
						func.item_tooltip(div,this.data[name])
					}
					var show_grade = this.grades.includes(key)
					if(show_grade){
						div.style.color = defs.item.grade_color[this.data[name].grade||0]
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
				var r = html.row(el,...data)
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
	}
}
