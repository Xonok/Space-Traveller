draw = {
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
	init(el,width,height){
		draw.canvas = el
		draw.ctx = draw.canvas.getContext("2d")
		draw.width = width
		draw.height = height
		var ctx = draw.ctx
		var scaling = 2
		draw.scaling = scaling
		var fillRect = ctx.fillRect
		var drawImage = ctx.drawImage
		var newFillRect = (x,y,w,h)=>{
			fillRect.call(ctx,x*scaling,y*scaling,w*scaling,h*scaling)
		}
		var newDrawImage = (img,x,y,w,h)=>{
			drawImage.call(ctx,img,x*scaling,y*scaling,w*scaling,h*scaling)
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
		ctx.drawAtlasImage = drawAtlasImage.bind(ctx)
		return ctx
	},
	load_imgs(entries){
		Object.entries(entries).forEach(e=>{
			draw.load_img(e[0],e[1])
		})
	},
	load_atlas_imgs(entries){
		Object.entries(entries).forEach(e=>{
			draw.load_atlas_img(e[0],e[1])
		})
	},
	load_img(name,path){
		var img = new Image()
		img.src = path
		img.promise = img.decode()
		draw.images[name] = img
	},
	load_atlas_img(name,path){
		var img = new Image()
		img.src = path
		img.promise = img.decode()
		img.remap2 = {
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
		img.promise.then(e=>{
			img.tiles_per_line = 4
			img.tile_width = img.naturalWidth / img.tiles_per_line
		})
		draw.images[name] = img
	},
	async load_done(){
		var promises = Object.values(draw.images).map(i=>i.promise)
		console.log(promises)
		await Promise.allSettled(promises)
	},
	img(src,x,y,w,r){
		var scaling = draw.scaling
		var ctx = draw.ctx
		var iteration = draw.iteration
		var draw = (r)=>{
			if(draw.iteration !== iteration){return}
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
		if(draw.images[src]){
			var img = draw.images[src]
			if(img.complete){
				draw(r)
			}
			else{
				img.addEventListener("load",()=>draw(r))
				img.addEventListener("error",()=>draw(r))
			}
		}
		else{
			var img = new Image()
			draw.images[src] = img
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
	clear(){
		var canvas = draw.canvas
		var ctx = draw.ctx
		var scaling = draw.scaling
		canvas.width = draw.width*scaling
		canvas.height = draw.height*scaling
		canvas.style.width = draw.width+"px"
		canvas.style.height = draw.height+"px"
		ctx.fillStyle = "black"
		ctx.fillRect(0,0,canvas.width,canvas.height)
	},
	async update(){
		var draw_tile = (x2,y2)=>{
			var up_left = tiles[x2-1]?.[Number(y2)+1]?.terrain || "deep_energy"
			var up_right = tiles[x2]?.[Number(y2)+1]?.terrain || "deep_energy"
			var bot_left = tiles[x2-1]?.[y2].terrain || "deep_energy"
			var bot_right = tiles[x2]?.[y2].terrain || "deep_energy"
			var x4 = x3-cell_width*0.5
			var y4 = y3-cell_width*0.5
			var bg_drawn = false
			draw.tile_data.forEach((name,img)=>{
				var idx = 0
				idx += up_left === name ? 8 : 0
				idx += up_right === name ? 4 : 0
				idx += bot_left === name ? 2 : 0
				idx += bot_right === name ? 1 : 0
				if(name === "space"){
					var img2 = draw.tile_data[name+"_var"]
					var rand_idx = f.squirrel_2d(Number(x2),Number(y2),f.str_to_int(pship.pos.system)) % 16
					if(img2.naturalHeight){
						ctx.drawAtlasImage(img2,rand_idx,x4,y4,cell_width,cell_width)
					}
					else{
						ctx.drawAtlasImage(img,0,x4,y4,cell_width,cell_width)
					}
				}
				if(!idx){return}
				if(!bg_drawn){
					bg_drawn = true
					var img2 = draw.tile_data[name+"_var"]
					var rand_idx = f.squirrel_2d(Number(x2),Number(y2),f.str_to_int(pship.pos.system)) % 16
					if(img2.naturalHeight){
						ctx.drawAtlasImage(img2,rand_idx,x4,y4,cell_width,cell_width)
					}
					else{
						ctx.drawAtlasImage(img,0,x4,y4,cell_width,cell_width)
					}
					
				}
				else{
					ctx.drawAtlasImage(img,idx,x4,y4,cell_width,cell_width)
				}
			})
		}
		if(!draw.loaded){
			console.log("Waiting for tilesets...")
			await draw.promise
		}
		var pship = q.ships[q.cdata.ship]
		var {x,y} = pship.pos
		draw.iteration++
		if(x !== undefined){
			draw.x = x
		}
		if(y !== undefined){
			draw.y = y
		}
		var tiles = q.tiles
		x = draw.x
		y = draw.y
		var canvas = draw.canvas
		var ctx = draw.ctx
		var cell_width = draw.cell_width
		var scaling = draw.scaling
		canvas.width = draw.width*scaling
		canvas.height = draw.width*scaling
		canvas.style.width = draw.width+"px"
		canvas.style.height = draw.width+"px"
		ctx.fillStyle = "black"
		ctx.clearRect(0,0,canvas.width,canvas.height)
		ctx.filter = "none"
		if(pship.pos.system.includes("DG")){
			ctx.filter = "brightness(0.9) contrast(1.1)"
		}
		var min_x = 0
		var max_x = 0
		var min_y = 0
		var max_y = 0
		for(let [x2,row] of Object.entries(tiles)){
			for(let [y2,tile] of Object.entries(row)){
				var x3 = (x2-x+q.vision)*cell_width
				var y3 = (y2-y-q.vision)*cell_width*-1
				draw.new_tiles && draw_tile(x2,y2)
			}
		}
		for(let [x2,row] of Object.entries(tiles)){
			for(let [y2,tile] of Object.entries(row)){
				var x3 = (x2-x+q.vision)*cell_width
				var y3 = (y2-y-q.vision)*cell_width*-1
				var color = draw.terrain_color[tile.terrain]
				ctx.fillStyle = color || "blue"
				!draw.new_tiles && ctx.fillRect(x3,y3,cell_width,cell_width)
				if(tile.structure){
					var structure_scaling = tile.structure.type === "planet" ? 1.3 : 1
					draw.img(tile.structure.img,x3+cell_width/2,y3+cell_width/2,cell_width*structure_scaling)
				}
				if(tile.img){
					draw.img(tile.img,x3+cell_width/2,y3+cell_width/2,cell_width)
				}
				if(!tile.structure && !tile.img && tile.ships /*&& (x !== 0 || y !== 0)*/){
					var ship_count = Object.keys(tile.ships).length
					var ship_spacing = cell_width*0.6/ship_count
					var ship_list = Array.from(Object.entries(tile.ships).map(e=>e[1])).sort((a,b)=>a.size-b.size)
					ship_list.forEach((e,idx)=>{
						var ship_entry = e
						var x_offset = cell_width*0.3*Math.cos(Math.PI*(idx/ship_count)*2)
						var y_offset = cell_width*0.3*Math.sin(Math.PI*(idx/ship_count)*2)
						if(ship_count === 1){
							x_offset = 0
							y_offset = 0
						}
						if(idx < 10){
							draw.img(ship_entry.img,x3+cell_width/2+x_offset,y3+cell_width/2+y_offset,cell_width,ship_entry.rotation)
						}
					})
				}
				if(!tile.structure && !tile.img && !tile.ships && tile.items /*&& (x !== 0 || y !== 0)*/){
					draw.img("img/loot.webp",x3+cell_width/2,y3+cell_width/2,cell_width)
				}
				min_x = Math.min(min_x,x2)
				max_x = Math.max(max_x,x2)
				min_y = Math.min(min_y,y2)
				max_y = Math.max(max_y,y2)
			}
		}
	}
}
