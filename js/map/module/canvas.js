map.canvas = {
	zoom: 0,
	zoom_step: 1.5,
	zoom_limit: 3,
	camera_x: 0,
	camera_y: 0,
	update(){
		if(f.view.active !== "map"){return}
		var show_all = false
		var data = q.star_data
		var star = q.pship.pos.system
		var canvas = window.canvas_map
		var ctx = canvas.getContext("2d")
		var w = canvas.clientWidth
		var h = canvas.clientHeight
		var scaling = 3000*map.canvas.zoom_step**map.canvas.zoom
		var link_colors = {
			"0": "blue",
			"1": "purple",
			"2": "green",
			"3": "turquoise"
		}
		canvas.width = w
		canvas.height = h
		
		ctx.fillStyle = "black"
		ctx.clearRect(0,0,map.width,map.height)
		
		var central = data.stars[star]
		// central = data.stars.Merak
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
			var x2 = -c_x+x+w/2-map.canvas.camera_x*map.canvas.zoom_step**map.canvas.zoom
			var y2 = -c_y+y+h/2-map.canvas.camera_y*map.canvas.zoom_step**map.canvas.zoom
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
			if(!show_all && d.no_map){return}
			if(!data.stars[name]){return}
			var [x,y] = coords_offset(data.stars[name])
			d.forEach((k,v)=>{
				if(k==="ra"||k==="dec"||k==="lvl"||k==="no_map"){return}
				if(!drawn_links[v]){
					var other = data.stars[v]
					if(!other){return}
					if(!other.ra || !other.dec){return}
					if(!show_all && other.no_map){return}
					var [x2,y2] = coords_offset(other)
					var lvl_max = Math.max(d.lvl || 0,other.lvl || 0)
					line(x,y,x2,y2,link_colors[lvl_max])
				}
				drawn_links[name] = true
			})
		}
		function draw_star(name,d){
			if(!d.ra || !d.dec){return}
			if(!show_all && d.no_map){return}
			var [x,y] = coords_offset(d)
			var color = name === star ? "red" : "green" 
			ctx.save()
			ctx.fillStyle = color
			ctx.fillRect(x-5,y-5,10,10)
			ctx.restore()
		}
		function draw_star_name(name,d){
			if(!d.ra || !d.dec){return}
			if(!show_all && d.no_map){return}
			var [x,y] = coords_offset(d)
			ctx.save()
			var txt_width = ctx.measureText(name).width
			ctx.fillStyle = "white"
			ctx.fillText(name,x-txt_width/2,y-6)
			ctx.restore()
		}
		
		data.stars.forEach(draw_links)
		data.stars.forEach(draw_star)
		data.stars.forEach(draw_star_name)
	},
	init(){
		var canvas = window.canvas_map
		var click_right = false
		canvas.onmousedown = e=>{
			// 0 is left, 1 is middle, 2 is right
			if(e.button === 2){
				click_right = true
				e.preventDefault()
			}
		}
		canvas.onmouseup = e=>{
			if(e.button === 2){
				click_right = false
				e.preventDefault()
			}
		}
		canvas.onmousemove = e=>{
			if(click_right){
				map.canvas.camera_x -= e.movementX/map.canvas.zoom_step**map.canvas.zoom
				map.canvas.camera_y -= e.movementY/map.canvas.zoom_step**map.canvas.zoom
				map.canvas.update()
				e.preventDefault()
			}
		}
		canvas.oncontextmenu = e=>{
			e.preventDefault()
		}
		canvas.onwheel = e=>{
			map.canvas.zoom += e.deltaY > 0 ? -1 : 1
			map.canvas.zoom = Math.min(map.canvas.zoom,map.canvas.zoom_limit)
			map.canvas.zoom = Math.max(map.canvas.zoom,-map.canvas.zoom_limit)
			map.canvas.update()
		}
		window.addEventListener("resize",map.canvas.update)
	}
}
map.canvas.init()