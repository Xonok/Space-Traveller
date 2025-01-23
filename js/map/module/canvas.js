map.canvas = {
	update(msg){
		var data = msg.star_data
		var canvas = window.canvas_map
		var ctx = canvas.getContext("2d")
		var w = 800
		var h = 600
		var scaling = 3000
		var link_colors = {
			"0": "blue",
			"1": "purple"
		}
		canvas.width = w
		canvas.height = h
		
		ctx.fillStyle = "black"
		ctx.clearRect(0,0,map.width,map.height)
		
		var central = data.stars[star]
		var [c_x,c_y] = coords(central)
		var drawn_links = {}
		
		function coords(d){
			var r_d = -(d.ra[0]+d.ra[1]/60)*15
			var x = (r_d/360)*scaling
			var dec_d = d.dec[0]+d.dec[1]/60
			var y = -(dec_d/360)*scaling
			return [x,y]
		}
		function coords_offset(d){
			var [x,y] = coords(d)
			var x2 = -c_x+x+w/2
			var y2 = -c_y+y+h/2
			return [x2,y2]
		}
		function line(x,y,x2,y2,color){
			ctx.save()
			ctx.strokeStyle = color
			ctx.beginPath()
			ctx.moveTo(x,y)
			ctx.lineTo(x2,y2)
			ctx.closePath()
			ctx.stroke()
			ctx.restore()
		}
		function draw_links(name,d){
			if(!d.ra || !d.dec){return}
			var [x,y] = coords_offset(data.stars[name])
			d.forEach((k,v)=>{
				if(k==="ra"||k==="dec"||k==="lvl"){return}
				if(!drawn_links[v]){
					var other = data.stars[v]
					if(!other.ra || !other.dec){return}
					var [x2,y2] = coords_offset(other)
					var lvl_max = Math.max(d.lvl || 0,other.lvl || 0)
					line(x,y,x2,y2,link_colors[lvl_max])
				}
				drawn_links[name] = true
			})
		}
		function draw_star(name,d){
			if(!d.ra || !d.dec){return}
			var [x,y] = coords_offset(d)
			var color = name === star ? "red" : "green" 
			ctx.save()
			ctx.fillStyle = color
			ctx.fillRect(x-5,y-5,10,10)
			ctx.restore()
		}
		function draw_star_name(name,d){
			if(!d.ra || !d.dec){return}
			var [x,y] = coords_offset(d)
			ctx.save()
			var txt_width = ctx.measureText(name).width
			ctx.fillStyle = "white"
			ctx.fillText(name,x-txt_width/2,y)
			ctx.restore()
		}
		
		data.stars.forEach(draw_links)
		data.stars.forEach(draw_star)
		data.stars.forEach(draw_star_name)
	}
}
