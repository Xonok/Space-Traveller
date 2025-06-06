func.theme = {
	update(el){
		el.classList.forEach(c=>{
			if(c.includes("theme_")){
				el.classList.remove(c)
			}
		})
		if(f.view.active === "dock"){
			var structure_theme = {
				"planet_ice": "theme_ice"
			}
			var shiptype = q.structure?.ship
			var theme_name = structure_theme[shiptype] || "theme_default"
			el.classList.add(theme_name)
		}
	}
}