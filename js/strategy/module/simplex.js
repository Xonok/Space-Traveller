strategy.simplex = {
	cache: {},
	ncache: {},
	hits: 0,
	misses: 0,
	gradients: [[1,1],[-1,1],[1,-1],[-1,-1],[1,0],[-1,0],[0,1],[0,-1]],
	dot(grad,x,y){return grad[0]*x+grad[1]*y},
	get(x,y,seed,scale,octaves){
		var result = 0
		var total_factor = 0
		for(var i=0;i<octaves;i++){
			var factor = 1/2**i
			result += strategy.simplex.noise(x*scale*2**i,y*scale*2**i,seed)*factor
			total_factor += factor
		}
		return result/total_factor
	},
	grid_gradient_idx(x,y,seed){
		var cache = strategy.simplex.cache
		var ensure = (table,val,def)=>{
			if(!table[val]){
				table[val] = def
			}
		}
		var idx = cache[seed]?.[x]?.[y]
		if(idx === undefined){
			idx = Math.floor(f.squirrel_2d_unit(x,y,seed)*strategy.simplex.gradients.length) % strategy.simplex.gradients.length
			ensure(cache,seed,{})
			ensure(cache[seed],x,{})
			ensure(cache[seed][x],y,idx)
			strategy.simplex.misses++
		}
		else{
			strategy.simplex.hits++
		}
		return idx
	},
	noise(x,y,seed){
		var strat = strategy.simplex
		var ensure = (table,val,def)=>{
			if(!table[val]){
				table[val] = def
			}
		}
		var x_cut = Math.round(x*300)
		var y_cut = Math.round(y*300)
		var result = strat.ncache[seed]?.[x_cut]?.[y_cut]
		if(result !== undefined){
			return result
		}
        // Skewing and unskewing factors for 2D
        var F2 = 0.5 * (Math.sqrt(3) - 1);
        var G2 = (3 - Math.sqrt(3)) / 6;

        // Skew the input space to determine the simplex cell
        var s = (x + y) * F2; // Skew factor
        var i = Math.floor(x + s);
        var j = Math.floor(y + s);

        // Unskew the cell origin back to (x, y) space
        var t = (i + j) * G2; // Unskew factor
        var X0 = i - t;
        var Y0 = j - t;

        // Distances from the cell origin
        var x0 = x - X0;
        var y0 = y - Y0;

        // Determine which simplex we are in
        var i1 = x0 > y0 ? 1 : 0; // Lower triangle
        var j1 = x0 > y0 ? 0 : 1; // Upper triangle

        // Offsets for the other simplex corners
        var x1 = x0 - i1 + G2;
        var y1 = y0 - j1 + G2;
        var x2 = x0 - 1 + 2 * G2;
        var y2 = y0 - 1 + 2 * G2;

        // Hash the corners of the simplex
        var ii = i & 255;
        var jj = j & 255;
		
		var gi0 = strat.grid_gradient_idx(ii,jj,seed)
		var gi1 = strat.grid_gradient_idx(ii+i1,jj+j1,seed)
		var gi2 = strat.grid_gradient_idx(ii+1,jj+1,seed)

        // Calculate contributions from each corner
        var t0 = 0.5 - x0 * x0 - y0 * y0;
        var n0 = t0 < 0 ? 0 : (t0 * t0) * strat.dot(strat.gradients[gi0], x0, y0);

        var t1 = 0.5 - x1 * x1 - y1 * y1;
        var n1 = t1 < 0 ? 0 : (t1 * t1) * strat.dot(strat.gradients[gi1], x1, y1);

        var t2 = 0.5 - x2 * x2 - y2 * y2;
        var n2 = t2 < 0 ? 0 : (t2 * t2) * strat.dot(strat.gradients[gi2], x2, y2);

        // Add contributions and scale the result
		
		result = (n0 + n1 + n2)*7
		ensure(strat.ncache,seed,{})
		ensure(strat.ncache[seed],x_cut,{})
		ensure(strat.ncache[seed][x_cut],y_cut,result)
        return result
	}
}

/*class SimplexNoise {
    constructor(seed,scaling) {
        // Gradient vectors for 2D
        this.gradients = [
            [1, 1], [-1, 1], [1, -1], [-1, -1],
            [1, 0], [-1, 0], [0, 1], [0, -1]
        ];
		this.grid_gradients = {}
		this.seed = seed
		this.scaling = scaling
    }

    dot(grad, x, y) {
        // Compute the dot product of gradient vector and distance vector
        return grad[0] * x + grad[1] * y;
    }

	grid_gradient_idx(x,y) {
		var idx = this.grid_gradients[y]?.[x]
		if(idx === undefined){
			var idx = Math.floor(f.squirrel_2d_unit(x,y,this.seed)*this.gradients.length) % this.gradients.length
			if(!this.grid_gradients[y]){
				this.grid_gradients[y] = {}
			}
			this.grid_gradients[y][x] = idx
		}
		return idx
	}

    noise(x, y) {
		x *= this.scaling
		y *= this.scaling
        // Skewing and unskewing factors for 2D
        const F2 = 0.5 * (Math.sqrt(3) - 1);
        const G2 = (3 - Math.sqrt(3)) / 6;

        // Skew the input space to determine the simplex cell
        const s = (x + y) * F2; // Skew factor
        const i = Math.floor(x + s);
        const j = Math.floor(y + s);

        // Unskew the cell origin back to (x, y) space
        const t = (i + j) * G2; // Unskew factor
        const X0 = i - t;
        const Y0 = j - t;

        // Distances from the cell origin
        const x0 = x - X0;
        const y0 = y - Y0;

        // Determine which simplex we are in
        const i1 = x0 > y0 ? 1 : 0; // Lower triangle
        const j1 = x0 > y0 ? 0 : 1; // Upper triangle

        // Offsets for the other simplex corners
        const x1 = x0 - i1 + G2;
        const y1 = y0 - j1 + G2;
        const x2 = x0 - 1 + 2 * G2;
        const y2 = y0 - 1 + 2 * G2;

        // Hash the corners of the simplex
        const ii = i & 255;
        const jj = j & 255;

        // var gi0 = this.p[this.p[ii] + jj] % this.gradients.length;
        // var gi1 = this.p[this.p[ii + i1] + jj + j1] % this.gradients.length;
        // var gi2 = this.p[this.p[ii + 1] + jj + 1] % this.gradients.length;
		
		var gi0 = this.grid_gradient_idx(ii,jj)
		var gi1 = this.grid_gradient_idx(ii+i1,jj+j1)
		var gi2 = this.grid_gradient_idx(ii+1,jj+1)

        // Calculate contributions from each corner
        const t0 = 0.5 - x0 * x0 - y0 * y0;
        const n0 = t0 < 0 ? 0 : (t0 * t0) * this.dot(this.gradients[gi0], x0, y0);

        const t1 = 0.5 - x1 * x1 - y1 * y1;
        const n1 = t1 < 0 ? 0 : (t1 * t1) * this.dot(this.gradients[gi1], x1, y1);

        const t2 = 0.5 - x2 * x2 - y2 * y2;
        const n2 = t2 < 0 ? 0 : (t2 * t2) * this.dot(this.gradients[gi2], x2, y2);

        // Add contributions and scale the result
        return (n0 + n1 + n2)*7; // Scale factor for normalization
    }
}*/

/*
// Example usage
const simplex = new SimplexNoise();
const width = 100, height = 100;
const scale = 0.1; // Adjust for frequency

// Generate a 2D grid of simplex noise
const noiseGrid = [];
for (let y = 0; y < height; y++) {
    const row = [];
    for (let x = 0; x < width; x++) {
        row.push(simplex.noise(x * scale, y * scale));
    }
    noiseGrid.push(row);
}

// Log or visualize the result
console.log(noiseGrid);
*/
