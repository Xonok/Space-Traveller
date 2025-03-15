var tiles_w = 60
var tiles_h = 40
var w = 1200
var h = 800
var tile_size = Math.min(Math.floor(w/tiles_w),Math.floor(h/tiles_h))
w = tile_size*tiles_w
h = tile_size*tiles_h
var scale = 1/30
var seed = 127

var seed1 = f.squirrel_5(0,seed)
var seed2 = f.squirrel_5(1,seed)
var seed3 = f.squirrel_5(2,seed)
var seed4 = f.squirrel_5(3,seed)
var seed5 = f.squirrel_5(4,seed)

var canvas = window.game_canvas
canvas.width = w
canvas.height = h
var tile_names = ["energy","space","nebula","asteroids","exotic","phase","deep_energy","energy_var","space_var","nebula_var","asteroids_var","exotic_var","phase_var","deep_energy_var"]
var tile_paths = Object.fromEntries(tile_names.map(n=>{
	return [n,"img/tiles/"+n+".webp"]
}))
var ctx = draw.init(canvas,w,h)
draw.load_atlas_imgs(tile_paths)
draw.load_img("beetle","img/beetle.webp")

var last_time
var frame_idx = 0
var max_dist = 0
var centerDist = (x,y)=>{
	var c_x = tiles_w/2
	var c_y = tiles_h/2
	var x_factor = 80/120*1.1
	var y_factor = 1.1
	return (((c_x-x)*x_factor)**2+((c_y-y)**2)*y_factor)**0.5
}
function do_draw(time){
	var d_t = 0
	if(last_time){
		d_t = time-last_time
	}
	
	var tileCheck = (noise,x,y,chance)=>{
		return (noise+1)/2<chance
	}
	var tile_color = {
		"deep_energy": [0,0,128],
		"energy": [50,200,256],
		"nebula": [256,0,0],
		"asteroids": [128,128,128],
		"exotic": [0,256,0],
		"phase": [255,165,0],
		"space": [0,0,0]
	}
	var tilePick = (x,y)=>{
		var border_factor = 0.5
		var d_freq = 0.4*(1-border_factor)
		var e_freq = 0.5*(1-border_factor)
		var dist = ((centerDist(x-frame_idx,y))/tiles_h)
		dist /= (1-dist)
		max_dist = Math.max(dist,max_dist)
		var noise = strategy.simplex.get(x,y,seed1,scale,5)
		var deep = tileCheck(noise,x,y,d_freq+dist*border_factor)
		var energy = tileCheck(noise,x,y,e_freq+dist*border_factor)
		if(!energy){
			for(var i=-1;i<2;i++){
				for(var j=-1;j<2;j++){
					var noise_n = strategy.simplex.get(x+i,y+j,seed1,scale,5)
					var dist2 = ((centerDist(x+i-frame_idx,y+j))/tiles_h)
					dist2 /= (1-dist2)
					if(tileCheck(noise_n,x+i,y+j,d_freq+dist2*border_factor)){
						energy = true
					}
				}
			}
		}
		if(deep){return "deep_energy"}
		if(energy){return "energy"}
		var noise2 = strategy.simplex.get(x,y,seed2,scale,5)
		var noise3 = strategy.simplex.get(x,y,seed3,scale,5)
		var nebula = tileCheck(noise2,x,y,0.35)
		var asteroid = tileCheck(noise3,x,y,0.35)
		if(nebula){return "nebula"}
		if(asteroid){return "asteroids"}
		var noise4 = strategy.simplex.get(x,y,seed4,scale,5)
		var noise5 = strategy.simplex.get(x,y,seed5,scale,5)
		var exo = tileCheck(noise4,x,y,0.25)
		var phase = tileCheck(noise5,x,y,0.25)
		if(exo){return "exotic"}
		if(phase){return "phase"}
		return "space"
	}
	var tileDraw = (x,y,tile_name,force_full=false)=>{
		if(draw.images[tile_name+"_var"]){
			var rand_idx = f.squirrel_2d(Number(x+frame_idx),Number(y),f.str_to_int("Default_System")) % 16
			ctx.drawAtlasImage(draw.images[tile_name+"_var"],rand_idx,x*tile_size,y*tile_size,tile_size,tile_size)
		}
		else{
			ctx.drawAtlasImage(draw.images[tile_name],0,x*tile_size,y*tile_size,tile_size,tile_size)
		}
	}
	var tileDrawStack = (x,y,force_full=false)=>{
		var tile_name = tilePick(x+frame_idx,y)
		var up_left = tilePick(x-1+frame_idx,Number(y)+1)
		var up_right = tilePick(x+frame_idx,Number(y)+1)
		var bot_left = tilePick(x-1+frame_idx,y)
		var bot_right = tilePick(x+frame_idx,y)
		var base_tiles = ["space","deep_energy"]
		base_tiles.forEach(t=>{
			if(t !== "space" && !up_left === t && !up_right === t && !bot_left === t && !bot_right === t){return}
			tileDraw(x,y,t,force_full)
		})
		if(draw.images[tile_name+"_var"]){
			var rand_idx = f.squirrel_2d(Number(x+frame_idx),Number(y),f.str_to_int("Default_System")) % 16
			ctx.drawAtlasImage(draw.images[tile_name+"_var"],rand_idx,x*tile_size,y*tile_size,tile_size,tile_size)
		}
		else{
			ctx.drawAtlasImage(draw.images[tile_name],0,x*tile_size,y*tile_size,tile_size,tile_size)
		}
	}
	draw.clear()
	for(var y=0;y<tiles_h;y++){
		for(var x=0;x<tiles_w;x++){
			// ctx.fillStyle = "rgb("+r+","+g+","+b+")"
			// ctx.fillRect(x*tile_size,y*tile_size,tile_size,tile_size)
			tileDrawStack(x,y)
		}
	}
	frame_idx++
	last_time = time
	var hits = strategy.simplex.hits
	var misses = strategy.simplex.misses
	window.frame_counter.innerHTML = frame_idx
	window.cache_counter.innerHTML = f.formatNumber(hits)+"/"+f.formatNumber(misses)+"("+Math.floor((misses/(misses+hits))*100000)/100000+")"
	window.fps_counter.innerHTML = d_t ? 1000/d_t : 0
	if(frame_idx < 1000){
		requestAnimationFrame(do_draw)
	}
}

async function run(){
	await draw.load_done()
	requestAnimationFrame(do_draw)
}

run()