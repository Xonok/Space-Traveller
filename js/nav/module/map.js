nav.map = {
	init(el,vision){
		nav.map.el = el
		nav.map.grid = {}
		nav.map.vision = vision
		el.innerHTML = ""
		var tiles_x = 1+vision*2
		var tiles_y = 1+vision*2
		var x_min = Math.floor(-(tiles_x-1)/2)
		var x_max = Math.floor((tiles_x+1)/2)
		var y_min = Math.floor(-(tiles_y-1)/2)
		var y_max = Math.floor((tiles_y+1)/2)
		for(let y = y_min;y<y_max;y++){
			var row = f.addElement(el,"tr")
			for(let x = x_min;x<x_max;x++){
				if(!nav.map.grid[x]){nav.map.grid[x]={}}
				var cell = f.addElement(row,"td")
				cell.coord_x = x
				cell.coord_y = y
				nav.map.grid[x][y] = cell
			}
		}
		if(!ship_img){
			ship_img = f.addElement(nav.map.grid[0][0],"img")
		}
	},
	update(x,y,tiles){
		var grid = nav.map.grid
		for(let [x2,row] of Object.entries(tiles)){
			for(let [y2,tile] of Object.entries(row)){
				var x3 = x2-x
				var y3 = y2-y
				if(!grid[x3]?.[y3]){continue}
				var cell = grid[x3][y3]
				color = terrain_color[tile.terrain]
				cell.style.backgroundColor = color
				cell.style.color = invertColour(color || "#0000FF")
				if(tile.variation){
					cell.style.backgroundImage = "url(/img/tiles/"+terrain_color_name[tile.terrain]+"/"+tile.variation+".png)"
				}
				else{
					cell.style.backgroundImage = null
				}
				Array.from(cell.childNodes).forEach(n=>{
					if(n.object || n.structure || n.ship || n.loot){
						n.remove()
					}
				})
				if(tile.structure){
					var structure_img = f.addElement(cell,"img")
					structure_img.src = tile.structure.image
					structure_img.structure = true
				}
				if(tile.img){
					var tile_img = f.addElement(cell,"img")
					tile_img.src = tile.img
					tile_img.object = true
				}
				if(!tile.structure && !tile.img && tile.ship && (x3 != 0 || y3 != 0)){
					var ship_img = f.addElement(cell,"img")
					ship_img.src = tile.ship.img
					ship_img.style = "transform: rotate("+String(tile.ship.rotation)+"deg);"
					ship_img.ship = true
				}
				if(!tile.structure && !tile.img && !tile.ship && tile.items && (x3 != 0 || y3 != 0)){
					var loot_img = f.addElement(cell,"img")
					loot_img.src = "img\\loot.webp"
					loot_img.loot = true
				}
			}
		}
	}
}
