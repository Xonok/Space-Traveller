func.dict = {
	recursive(table,...keys){
		keys.forEach(k=>{
			if(!table[k]){
				table[k] = {}
			}
			table = table[k]
		})
	}
}