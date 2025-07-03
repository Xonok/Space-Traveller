nav.starmap = {
	update(){
		var canvas = window.starmap
		var ctx = canvas.getContext("2d")
		canvas.width = 120
		canvas.height = 120
		canvas.style.border = "1px solid white"
		canvas.style.marginLeft = "1rem"
		var px = q.pship.pos.x
		var py = q.pship.pos.y
		ctx.fillStyle = "red"
		ctx.fillRect(canvas.width/2-5,canvas.height/2-5,10,10)
		Object.entries(q.star_wormholes).forEach(e=>{
			var key = e[0]
			var data = e[1]
			var target = data.target?.system
			if(!target){return}
			if(target === q.pship.pos.system){return}
			var angle = Math.atan2(data.y-py,data.x-px)
			var x = canvas.width/2+50*Math.cos(angle)
			var y = canvas.height/2-50*Math.sin(angle)
			var txt_width = ctx.measureText(target).width
			ctx.fillStyle = "white"
			ctx.fillText(target,x-txt_width/2,y)
		})
		
		//Calculate angle to each wormhole from ship
	}
}
query.register(nav.starmap.update,"tiles")