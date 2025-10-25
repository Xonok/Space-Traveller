query = {
	data: {
		stars: {},
		requesting: {},
		moving: {}
	},
	events: {},
	receive(msg){
		//Make a function for each query that exists.
		//Have the server send a list of query names,
		//error here if the function doesn't exist.
		//Each function should determine what idata can be extracted from the query response.
		//Once all parts of the message have been analyzed, send a single request for idata.
		//While idata isn't available, don't run any view-specific code.
		//It would be nice if there was a distinction between query responses and command responses.
		Object.entries(msg).forEach(e=>query.data[e[0].replace("-","_")] = e[1])
		Object.keys(msg).forEach(k=>{
			if(query.events[k]){
				query.events[k].forEach(e=>e(msg,query.data))
			}
		})
	},
	register(func,...names){
		names.forEach(n=>{
			if(!query.events[n]){
				query.events[n] = []
			}
			query.events[n].push(func)
		})
	}
}
var q = query.data