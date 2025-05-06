//Ülesannete formaat
//0 - täis lahendus
//1 - esialgsed numbrid
//
//Mõlemad on ridahaaval. Märk | tähendab järgmist lahtrit.
//Igas reas peab | märke olema sama palju.
//Tühjad lahtrid on kas eimiski või n. (n tähendab null, ehk eimiski)

var puzzles = {
	example: {
		"size": 5, //Mis on küljepikkus?
		"full": [
			"1|2|3|4|5",
			"2|3|4|5|1",
			"3|4|5|1|2",
			"4|5|1|2|3",
			"5|1|2|3|4"
		],
		"initial": [
			"|2|||5",
			"|||5|",
			"||||",
			"n|n|n|n|n",
			"5||||"
		]
	}
}
