func.input = {
	mousedown: 0,
	mouseup_promise: null,
	do_mousedown(){
		var resolve,reject
		func.input.mouseup_promise = new Promise((r1,r2)=>{resolve=r1;reject=r2})
		func.input.mouseup_promise.resolve = resolve
		func.input.mouseup_promise.reject = reject
		func.input.mousedown++
	},
	do_mouseup(){
		func.input.mouseup_promise.resolve()
		func.input.mousedown--
	},
	async wait_mouseup(){
		if(func.input.mouseup_promise){
			await func.input.mouseup_promise
		}
	}
}
document.body.onmousedown = func.input.do_mousedown
document.body.onmouseup = func.input.do_mouseup