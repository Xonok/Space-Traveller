// strategy.simplex.get(0,0,127,0.001,5)

var w = 1200
var h = 800
var scale = 1/100
var seed = 127

var canvas = window.game_canvas
var ctx = canvas.getContext("2d")
canvas.width = w
canvas.height = h

var last_time
var frame_idx = 0
function do_draw(time){
	var d_t = 0
	if(last_time){
		d_t = time-last_time
	}
	
	ctx.save()
	ctx.clearRect(0,0,w,h)
	var image_data = ctx.createImageData(w,h)
	var data = image_data.data

	var setPixel = (x,y,r,g,b,a)=>{
		var index = (y * w + x) * 4 // Calculate the index in the data array
		data[index] = r
		data[index + 1] = g
		data[index + 2] = b
		data[index + 3] = a
	}
	for(var y=0;y<h;y++){
		for(var x=0;x<w;x++){
			var noise = strategy.simplex.get(x+frame_idx,y,seed,scale,5)
			var r = noise*128+128
			var g = noise*128+128
			var b = noise*128+128
			setPixel(x, y, r, g, b, 255)
		}
	}
	ctx.putImageData(image_data, 0, 0)
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