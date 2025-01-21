map.canvas = {
	update(msg){
		var data = msg.star_data
		var canvas = window.canvas_map
		var ctx = canvas.getContext("2d")
		var w = 800
		var h = 600
		var scaling = 3000
		canvas.width = w
		canvas.height = h
		
		ctx.fillStyle = "black"
		ctx.clearRect(0,0,map.width,map.height)
		
		var central = data.stars[star]
		var c_x = ra_coord(central.ra)
		var c_y = dec_coord(central.dec)
		
		function ra_coord(list){
			var r_d = -(list[0]+list[1]/60)*15
			return (r_d/360)*scaling
		}
		function dec_coord(list){
			var dec = list[0]+list[1]/60
			return -(dec/360)*scaling
		}
		function draw_star(ra,dec,name,color){
			var x = ra_coord(ra)
			var y = dec_coord(dec)
			var x2 = -c_x+x+w/2
			var y2 = -c_y+y+h/2
			var txt_width = ctx.measureText(name).width
			ctx.fillStyle = color
			ctx.fillRect(x2-5,y2-5,10,10)
			ctx.fillStyle = "white"
			ctx.fillText(name,x2-txt_width/2,y2)
		}
		
		data.stars.forEach((name,d2)=>{
			if(d2.ra && d2.dec){
				draw_star(d2.ra,d2.dec,name,"green")
			}
		})
		draw_star(central.ra,central.dec,"","red")
	}
}
