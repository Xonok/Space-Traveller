/*
Squirrel hash 5 by Squirrel Eiserloh.
Adapted for JS.
*/
var squirrel = {
	hash_1d(positionX,seed){
		var SQ5_BIT_NOISE1 = 0xd2a80a3f // 11010010101010000000101000111111
		var SQ5_BIT_NOISE2 = 0xa884f197 // 10101000100001001111000110010111
		var SQ5_BIT_NOISE3 = 0x6C736F4B // 01101100011100110110111101001011
		var SQ5_BIT_NOISE4 = 0xB79F3ABB // 10110111100111110011101010111011
		var SQ5_BIT_NOISE5 = 0x1b56c4f5 // 00011011010101101100010011110101
		
		var mangledBits = positionX >>> 0 // Ensure unsigned integer
		mangledBits *= SQ5_BIT_NOISE1
		mangledBits += seed
		mangledBits ^= (mangledBits >>> 9)
		mangledBits += SQ5_BIT_NOISE2
		mangledBits ^= (mangledBits >>> 11)
		mangledBits *= SQ5_BIT_NOISE3
		mangledBits ^= (mangledBits >>> 13)
		mangledBits += SQ5_BIT_NOISE4
		mangledBits ^= (mangledBits >>> 15)
		mangledBits *= SQ5_BIT_NOISE5
		mangledBits ^= (mangledBits >>> 17)
		
		return mangledBits >>> 0 // Ensure unsigned integer
	},
	hash_2d(indexX,indexY,seed){
		var PRIME_NUMBER = 198491317 // Large prime number with non-boring bits
		return squirrel.hash_1d(indexX + (PRIME_NUMBER * indexY), seed)
	},
	hash_2d_unit(indexX,indexY,seed){
		const ONE_OVER_MAX_UINT = 1.0 / 0xFFFFFFFF // Precomputed constant
		return ONE_OVER_MAX_UINT * squirrel.hash_2d(indexX, indexY, seed)
	}
}