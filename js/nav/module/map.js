nav.map = {
	//Keeping this part for now because it shows how to make dynamic CSS
	// td_rules: [],
	last_width: 0,
	width: 0,
	cell_width: 50,
	images: {},
	tile_data: {},
	iteration: 0,
	new_tiles: true,
	terrain_color: {
		"energy":"#00bfff",
		"space":"#000000",
		"nebula":"#ff0000",
		"asteroids":"#808080",
		"exotic":"#7cfc00",
		"phase":"#ffa500"
	},
	terrain_color_name: {
		"energy": "LightBlue",
		"space": "Black",
		"nebula": "Red",
		"asteroids": "Grey",
		"exotic": "Green",
		"phase": "Yellow"
	},
	terrain_name: {
		"energy": "Energy",
		"space": "Space",
		"nebula": "Nebula",
		"asteroids": "Asteroids",
		"exotic": "Exotic",
		"phase": "Phase"
	},
	init(el){
		if(nav.map.promise){return}
		el.innerHTML = ""
		nav.map.el = el
		nav.map.canvas = f.addElement(el,"canvas")
		nav.map.ctx = nav.map.canvas.getContext("2d")
		nav.map.canvas.style.border = "0.5px solid green"
		nav.map.canvas.classList.add("cursor_pointer")
		window.addEventListener('resize',nav.map.resize)
		var ctx = nav.map.ctx
		//Override functions to support scaling
		var scaling = 2
		nav.map.scaling = scaling
		var fillRect = ctx.fillRect
		var drawImage = ctx.drawImage
		var moveTo = ctx.moveTo
		var lineTo = ctx.lineTo
		var newFillRect = (x,y,w,h)=>{
			fillRect.call(ctx,x*scaling,y*scaling,w*scaling,h*scaling)
		}
		var newDrawImage = (img,x,y,w,h)=>{
			drawImage.call(ctx,img,x*scaling,y*scaling,w*scaling,h*scaling)
		}
		var newMoveTo = (x,y)=>{
			moveTo.call(ctx,x*scaling,y*scaling)
		}
		var newLineTo = (x,y)=>{
			lineTo.call(ctx,x*scaling,y*scaling)
		}
		var drawAtlasImage = (img,idx,x,y,w,h)=>{
			var tile_width = img.tile_width
			var tiles_per_line = img.tiles_per_line
			if(img.remap){
				if(img.remap[idx] !== undefined){
					idx = img.remap[idx]
				}
			}
			var atlas_x = (idx % tiles_per_line) * tile_width+1
			var atlas_y = Math.floor(idx / tiles_per_line) * tile_width+1
			var s_w = img.tile_width-2
			var s_h = img.tile_width-2
			var d_x = x*scaling
			var d_y = y*scaling
			var d_w = w*scaling
			var d_h = h*scaling
			drawImage.call(ctx,img,atlas_x,atlas_y,s_w,s_h,d_x,d_y,d_w,d_h)
		}
		ctx.fillRect = newFillRect.bind(ctx)
		ctx.drawImage = newDrawImage.bind(ctx)
		ctx.moveTo = newMoveTo.bind(ctx)
		ctx.lineTo = newLineTo.bind(ctx)
		ctx.drawAtlasImage = drawAtlasImage.bind(ctx)
		//!override
		//load tilesheets
		var tile_names = ["space","energy","asteroids","exotic","nebula","phase","deep_energy"]
		var promises = tile_names.map(n=>{
			var img = new Image()
			nav.map.tile_data[n] = img
			img.tiles_per_line = 4
			if(n === "exotic"){
				/*img.remap = {
					"1": 0,
					"7": 1,
					"11": 2,
					"2": 3,
					"5": 4,
					"0": 5,
					"15": 6,
					"10": 7,
					"4": 8,
					"13": 9,
					"14": 10,
					"8": 11,
					"6": 12,
					"12": 13,
					"9": 14,
					"3": 15
				}*/
				img.remap = {
					"1": 0,
					"7": 1,
					"11": 2,
					"2": 3,
					"5": 4,
					"0": 5,
					"15": 6,
					"10": 7,
					"4": 12,
					"13": 9,
					"14": 10,
					"8": 14,
					"6": 8,
					"12": 13,
					"9": 11,
					"3": 15
				}
			}
			
			img.src = "img/tiles/"+n+".webp"
			return img.decode()
		})
		var promises2 = tile_names.map(n=>{
			var img = new Image()
			nav.map.tile_data[n+"_var"] = img
			img.tiles_per_line = 4
			// img.src = "img/tiles/energy.webp"
			img.src = "img/tiles/"+n+"_var.webp"
			return img.decode()
		})
		nav.map.promise = Promise.allSettled([...promises,...promises2]).then(()=>{
			console.log("Tilesets loaded.")
			nav.map.loaded=true
			nav.map.tile_data.forEach((name,img)=>{
				img.tile_width = img.naturalWidth / img.tiles_per_line
			})
		})
	},
	img(src,x,y,w,r){
		var scaling = nav.map.scaling
		var ctx = nav.map.ctx
		var iteration = nav.map.iteration
		var draw = (r)=>{
			if(nav.map.iteration !== iteration){return}
			if(!img.naturalHeight){
				ctx.fillStyle = "pink"
				ctx.fillRect(x-w/2+0.5,y-w/2+0.5,w-1,w-1)
				return
			}
			var max_side = Math.max(img.naturalWidth,img.naturalHeight)
			var scale = w/max_side
			var w_scaled = Math.ceil(img.naturalWidth*scale)
			var h_scaled = Math.ceil(img.naturalHeight*scale)
			var scaling2 = (Math.max(img.naturalWidth,img.naturalHeight)/Math.min(img.naturalWidth,img.naturalHeight))**0.3
			if(r){
				var r_a = (r*Math.PI)/180
				ctx.save()
				ctx.translate(x*scaling,y*scaling)
				ctx.rotate(r_a)
				ctx.drawImage(img,-w_scaled/2*scaling2,-h_scaled/2*scaling2,w_scaled*scaling2,h_scaled*scaling2)
				ctx.restore()
			}
			else{
				ctx.drawImage(img,x-w_scaled/2*scaling2,y-h_scaled/2*scaling2,w_scaled*scaling2,h_scaled*scaling2)
			}
		}
		var img
		if(nav.map.images[src]){
			img = nav.map.images[src]
			if(img.complete){
				draw(r)
			}
			else{
				img.addEventListener("load",()=>draw(r))
				img.addEventListener("error",()=>draw(r))
			}
		}
		else{
			img = new Image()
			nav.map.images[src] = img
			img.src = src
			if(img.complete){
				draw(r)
			}
			else{
				img.addEventListener("load",()=>draw(r))
				img.addEventListener("error",()=>draw(r))
			}
		}
	},
	async update(){
		if(f.view.active !== "nav"){return}
		if(!q.pship){return}
		if(q.stars[q.pship.pos.system]?.checksum !== q.checksum_map){
			f.send("get-map",{"star":q.pship.pos.system})
			return
		}
		//Draw map multiple times using movement path, each time only changing centre coordinates.
		var time = Math.max(q.delay-Date.now()/1000+func.time.offset,0.1)
		var {x,y,rotation} = q.pship.pos
		var prev_x = nav.map.x !== undefined ? nav.map.x : x
		var prev_y = nav.map.y !== undefined ? nav.map.y : y
		var prev_r = nav.map.r !== undefined ? nav.map.r : rotation
		nav.map.iteration++
		if(x !== undefined){
			nav.map.x = x
		}
		if(y !== undefined){
			nav.map.y = y
		}
		if(rotation !== undefined){
			nav.map.r = rotation
		}
		x = nav.map.x
		y = nav.map.y
		r = nav.map.r
		var dx = x-prev_x
		var dy = y-prev_y
		var dr = r-prev_r
		if(dr > 180){
			dr = dr-360
		}
		if(dr < -180){
			dr = dr+360
		}
		if(dx === 0 && dy === 0){
			time = 0
		}
		if(q.pship.pos.system !== nav.map.system){
			time = 0
		}
		nav.map.system = q.pship.pos.system
		var total_iterations = Math.floor(time/0.03)
		var iteration = 0
		var should_stop = false
		if(time){
			var start_time = performance.now()
			nav.map.timer = setTimeout(()=>{should_stop = true},time*1000)
			var callback = time2=>{
				var d_t = Math.min((time2-start_time)/1000,time)
				d_t = Math.max(d_t,0)
				
				if(should_stop){
					nav.map.update2(x,y,r)
				}
				else{
					var x2 = prev_x+dx/time*d_t
					var y2 = prev_y+dy/time*d_t
					var r2 = prev_r+dr/time*d_t
					nav.map.update2(x2,y2,r2,true)
					requestAnimationFrame(callback)
				}
			}
			requestAnimationFrame(callback)
		}
		else{
			nav.map.update2(x,y,r)
		}
		
	},
	async update2(x,y,r,intermediate=false){
		var resource_alpha = false
		var draw_tile = (x2,y2)=>{
			var tiles2 = q.stars[q.pship.pos.system].tiles
			var up_left = tiles2[x2-1]?.[Number(y2)+1]?.terrain || "deep_energy"
			var up_right = tiles2[x2]?.[Number(y2)+1]?.terrain || "deep_energy"
			var bot_left = tiles2[x2-1]?.[y2]?.terrain || "deep_energy"
			var bot_right = tiles2[x2]?.[y2]?.terrain || "deep_energy"
			var x4 = x3-cell_width*0.5
			var y4 = y3-cell_width*0.5
			var rand_idx = f.squirrel_2d(Number(x2),Number(y2),f.str_to_int(q.pship.pos.system)) % 16
			nav.map.tile_data.forEach((name,img)=>{
				var idx = 0
				idx += up_left === name ? 8 : 0
				idx += up_right === name ? 4 : 0
				idx += bot_left === name ? 2 : 0
				idx += bot_right === name ? 1 : 0
				var img2 = nav.map.tile_data[name+"_var"]
				if(name === "space"){
					img2 = nav.map.tile_data[name+"_var"]
					if(img2.naturalHeight){
						ctx.drawAtlasImage(img2,rand_idx,x4,y4,cell_width,cell_width)
					}
					else{
						ctx.drawAtlasImage(img,0,x4,y4,cell_width,cell_width)
					}
					if(![up_left,up_right,bot_left,bot_right].find(e=>e !== "energy" && e !== "deep_energy")){
						var img2 = nav.map.tile_data["deep_energy_var"]
						if(img2.naturalHeight){
							ctx.drawAtlasImage(img2,rand_idx,x4,y4,cell_width,cell_width)
						}
						else{
							ctx.drawAtlasImage(nav.map.tile_data["deep_energy"],0,x4,y4,cell_width,cell_width)
						}
					}
				}
				if(!idx){return}
				ctx.save()
				if(bot_right === name){
					if(resource_alpha){
						ctx.globalAlpha = tiles[x2]?.[y2].res
					}
				}
				if(name !== "space"){
					if(idx === 15){
						if(img2.naturalHeight){
							ctx.drawAtlasImage(img2,rand_idx,x4,y4,cell_width,cell_width)
						}
					}
					else{
						ctx.drawAtlasImage(img,idx,x4,y4,cell_width,cell_width)
					}
				}
				ctx.restore()
			})
		}
		if(!nav.map.loaded){
			console.log("Waiting for tilesets...")
			await nav.map.promise
		}
		var tiles = q.tiles
		var canvas = nav.map.canvas
		var ctx = nav.map.ctx
		var cell_width = nav.map.cell_width
		var scaling = nav.map.scaling
		canvas.width = nav.map.width*scaling
		canvas.height = nav.map.width*scaling
		canvas.style.width = nav.map.width+"px"
		canvas.style.height = nav.map.width+"px"
		ctx.fillStyle = "black"
		ctx.clearRect(0,0,canvas.width,canvas.height)
		ctx.filter = "none"
		if(q.pship.pos.system.includes("DG")){
			ctx.filter = "brightness(0.9) contrast(1.1)"
		}
		var min_x = 0
		var max_x = 0
		var min_y = 0
		var max_y = 0
		var left_x = Math.floor(x)-q.vision-1
		var right_x = Math.floor(x)+q.vision+3
		var up_y = Math.floor(y)-q.vision-1
		var down_y = Math.floor(y)+q.vision+2
		for(let x2=left_x;x2<right_x;x2++){
			for(let y2=up_y;y2<down_y;y2++){
				var x3 = Math.floor((x2-x+q.vision)*cell_width)
				var y3 = Math.floor((y2-y-q.vision)*cell_width*-1)
				nav.map.new_tiles && draw_tile(x2,y2)
			}
		}
		for(let [x2,row] of Object.entries(tiles)){
			for(let [y2,tile] of Object.entries(row)){
				var x3 = (x2-x+q.vision)*cell_width
				var y3 = (y2-y-q.vision)*cell_width*-1
				var color = nav.map.terrain_color[tile.terrain]
				ctx.fillStyle = color || "blue"
				!nav.map.new_tiles && ctx.fillRect(x3,y3,cell_width,cell_width)
				if(tile.structure){
					var structure_scaling = tile.structure.type === "planet" ? 1.3 : 1
					nav.map.img(tile.structure.img,x3+cell_width/2,y3+cell_width/2,cell_width*structure_scaling)
				}
				if(tile.landmark){
					nav.map.img(tile.landmark.img,x3+cell_width/2,y3+cell_width/2,cell_width)
				}
				if(tile.img){
					nav.map.img(tile.img,x3+cell_width/2,y3+cell_width/2,cell_width)
				}
				if(!tile.structure && !tile.landmark && !tile.img && !tile.ships && tile.items /*&& (x !== 0 || y !== 0)*/){
					nav.map.img("img/loot.webp",x3+cell_width/2,y3+cell_width/2,cell_width)
				}
				min_x = Math.min(min_x,x2)
				max_x = Math.max(max_x,x2)
				min_y = Math.min(min_y,y2)
				max_y = Math.max(max_y,y2)
			}
		}
		var pos_tiles = {}
		q.positions?.forEach((sname,data)=>{
			if(q.cdata.ships.includes(sname)){return}
			var x_d = data.x-x
			var y_d = data.y-y
			var dist = Math.max(Math.abs(x_d),Math.abs(y_d))-1
			if(dist > q.vision){return}
			if(!pos_tiles[data.x]){
				pos_tiles[data.x] = {}
			}
			if(!pos_tiles[data.x][data.y]){
				pos_tiles[data.x][data.y] = {}
			}
			pos_tiles[data.x][data.y][sname] = data
		})
		for(let [x2,row] of Object.entries(pos_tiles)){
			x2 = Number(x2)
			for(let [y2,ptile] of Object.entries(row)){
				y2 = Number(y2)
				var tile = tiles[x2]?.[y2] || {}
				if(tile.structure || tile.img){continue}
				var x3 = (x2-x+q.vision)*cell_width
				var y3 = (y2-y-q.vision)*cell_width*-1
				var ship_count = Object.keys(ptile).length
				var ship_list = Array.from(Object.entries(ptile).map(e=>e[1])).sort((a,b)=>a.size-b.size)
				var idx = 0
				ptile.forEach((sname,data)=>{
					var img = q.idata[data.type].img
					var x_offset = cell_width*0.3*Math.cos(Math.PI*(idx/ship_count)*2)
					var y_offset = cell_width*0.3*Math.sin(Math.PI*(idx/ship_count)*2)
					if(ship_count === 1){
						x_offset = 0
						y_offset = 0
					}
					
					if(!tile.structure && !tile.img){
						if(idx < 10){
							nav.map.img(img,x3+cell_width/2+x_offset,y3+cell_width/2+y_offset,cell_width,data.rotation)
						}
					}
					idx++
				})
			}
		}
		var fleet_ships = {}
		q.positions?.forEach((sname,data)=>{
			if(!q.cdata.ships.includes(sname)){return}
			fleet_ships[sname] = data
		})
		var count_fleet = Object.keys(fleet_ships).length
		var idx_owned = 0
		fleet_ships.forEach((sname,data)=>{
			var tile = tiles[data.x]?.[data.y] || {}
			var img = q.idata[data.type].img
			var x_offset = cell_width*0.3*Math.cos(Math.PI*(idx_owned/count_fleet)*2)
			var y_offset = cell_width*0.3*Math.sin(Math.PI*(idx_owned/count_fleet)*2)
			if(count_fleet === 1){
				x_offset = 0
				y_offset = 0
			}
			var x4 = nav.map.width/2-cell_width/2
			var y4 = nav.map.width/2-cell_width/2
			var rotation = r
			if((!tile.structure && !tile.img) || (intermediate)){
				if(idx_owned < 10){
					nav.map.img(img,x4+cell_width/2+x_offset,y4+cell_width/2+y_offset,cell_width,rotation)
				}
			}
			idx_owned++
		})
		var line = (x,y,x2,y2)=>{
			ctx.strokeStyle = "green"
			ctx.lineWidth = 1*scaling
			ctx.beginPath()
			ctx.moveTo(x,y)
			ctx.lineTo(x2,y2)
			ctx.stroke()
		}
		for(let i = 0; i < q.vision*2+2; i++){
			//Horizontal
			// line(0,0+cell_width*i,canvas.width,0+cell_width*i)
			//Vertical
			// line(0+cell_width*i,0,0+cell_width*i,canvas.height)
		}
	},
	resize(){
		var style = window.getComputedStyle(window.map_container)
		var left = parseFloat(style.marginLeft)
		var right = parseFloat(style.marginRight)
		var fill_ratio = 0.7
		var box_width = (window.map_container.offsetWidth+left+right)*fill_ratio
		var side_length = q.vision*2+1
		var min_container_width = 350/side_length
		var max_width = Math.max(window.innerHeight/side_length*fill_ratio,min_container_width)
		var width = Math.min(Math.max(min_container_width,box_width/side_length),max_width)
		if(!nav.map.last_width || Math.abs(nav.map.last_width-width) > 0.1){
			nav.map.cell_width = Math.floor(width)
			nav.map.width = Math.floor(nav.map.cell_width*side_length)
			nav.map.update()
			f.forClass("info_display",e=>{
				e.style.width = Math.floor(width*side_length)+"px"
			})
			nav.map.last_width = width
			return true
		}
		return false
	},
	recv_map(){
		q.star.checksum = q.checksum_map
		q.stars[q.pship.pos.system] = q.star
	}
}
query.register(nav.map.recv_map,"star")