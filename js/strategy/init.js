// strategy.simplex.get(0,0,127,0.001,5)

var tiles_w = 120
var tiles_h = 80
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

var canvas = window.game_canvas
var ctx = canvas.getContext("2d")
canvas.width = w
canvas.height = h

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
	
	ctx.save()
	ctx.clearRect(0,0,w,h)
	// var image_data = ctx.createImageData(w,h)
	// var data = image_data.data

	var setPixel = (x,y,r,g,b,a)=>{
		var index = (y * w + x) * 4 // Calculate the index in the data array
		data[index] = r
		data[index + 1] = g
		data[index + 2] = b
		data[index + 3] = a
	}
	var tileCheck = (noise,x,y,chance)=>{
		return (noise+1)/2<chance
	}
	
	var tilePick = (x,y)=>{
		var dist = ((centerDist(x-frame_idx,y))/tiles_h)
		dist /= (1-dist)
		max_dist = Math.max(dist,max_dist)
		var noise = strategy.simplex.get(x,y,seed1,scale,5)
		var deep = tileCheck(noise,x,y,0.40+dist*0.3)
		var energy = tileCheck(noise,x,y,0.45+dist*0.3)
		if(deep){return [0,0,128]}
		if(energy){return [50,200,256]}
		var noise2 = strategy.simplex.get(x,y,seed2,scale,5)
		var noise3 = strategy.simplex.get(x,y,seed3,scale,5)
		var nebula = tileCheck(noise2,x,y,0.35)
		var asteroid = tileCheck(noise3,x,y,0.35)
		var exo = false
		var phase = false
		if(nebula){return [256,0,0]}
		if(asteroid){return [128,128,128]}
		if(exo){return [0,256,0]}
		if(phase){return [0,256,256]}
		return [0,0,0]
	}
	for(var y=0;y<tiles_h;y++){
		for(var x=0;x<tiles_w;x++){
			var [r,g,b] = tilePick(x+frame_idx,y)
			ctx.fillStyle = "rgb("+r+","+g+","+b+")"
			ctx.fillRect(x*tile_size,y*tile_size,tile_size,tile_size)
			// setPixel(x, y, r, g, b, 255)
		}
	}
	// ctx.putImageData(image_data, 0, 0)
	ctx.restore()
	frame_idx++
	last_time = time
	var hits = strategy.simplex.hits
	var misses = strategy.simplex.misses
	window.frame_counter.innerHTML = frame_idx
	window.cache_counter.innerHTML = f.formatNumber(hits)+"/"+f.formatNumber(misses)+"("+Math.floor((misses/(misses+hits))*100000)/100000+")"
	window.fps_counter.innerHTML = d_t ? 1000/d_t : 0
	if(frame_idx < 100){
		requestAnimationFrame(do_draw)
	}
}

requestAnimationFrame(do_draw)

//Canvas dimensions
//Ctx
//Generate grid
//Create image data
//Draw on image data
//Paste to canvas
//All of that in a loop probably