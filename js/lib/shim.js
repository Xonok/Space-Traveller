Object.getPrototypeOf([]).last = function(){return this[this.length-1]}
Object.getPrototypeOf([]).remove = function(e){return this.splice(this.indexOf(e),1)}
Object.getPrototypeOf({}).forEach = function(c){Object.entries(this).forEach(e=>c(e[0],e[1]))}
Object.getPrototypeOf({}).map = function(c){return Object.fromEntries(Object.entries(this).map(e=>[e[0],c(e[1])]))}
