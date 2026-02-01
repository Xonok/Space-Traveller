func.loc = {
	tile_ships: {},
	tile_structs: {},
	tile_landmarks: {},
	recv_pos(data,clear=false){
		var update = (entries,table)=>{
			if(!entries){return}
			entries.forEach((id,pos)=>{
				var {x,y,type} = pos
				// tile = table[x]?.[y]?.[cname]
				tile = table[x]?.[y]
				if(tile){
					tile.remove(id)
				}
				new_tile = table[x]?.[y] || []
				// func.dict.recursive(table,x,y,cname)
				// table[x][y][cname] = new_tile
				func.dict.recursive(table,x,y)
				table[x][y] = new_tile
			})
		}
		if(clear){
			if(data.positions){
				func.loc.tile_ships = {}
			}
			if(data.struct_positions){
				func.loc.tile_structs = {}
			}
			if(data.landmark_positions){
				func.loc.tile_landmarks = {}
			}
		}
		update(data.positions,func.loc.tile_ships)
		update(data.struct_positions,func.loc.tile_structs)
		update(data.landmark_positions,func.loc.tile_landmarks)
		console.log(data)
		query.receive(data)
		nav.map.should_draw = true
	},
	recv_ship_pos(data){
		query.receive(data)
		nav.map.should_draw = true
	},
	recv_struct_pos(data){
		
	},
	rect_landmark_pos(data){
		
	}
}