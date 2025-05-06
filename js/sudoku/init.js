sudoku.init = ()=>{
	console.log("page init done")
}

//(Vaata sudoku/module/puzzles.js faili, et näha formaati)
var puzzle = puzzles["example"]

//Kui sisse loed siis tahad formaati kus on pmst nii:
//grid[x][y] = val
//Aga esialgu on lihtsalt:
var grid = {}

//Selle saavutamiseks on vaja sisse lugeda vastavalt. Vaja 2 üksteise sees olevat loopi: y ja siis x.
puzzle.initial.forEach((line,row_idx)=>{
	//Spliti line ära | järgi
	//Siis loopi üle tokenite mis nii saad.
	//Fulli esimese rea splittimise tulemus peaks olema ["1","2","3","4","5"]
	//Initiali esimese rea splittimine peaks andma ["","2","","","","5"]
	
	tokens.forEach((val,col_idx)=>{
		//col_idx on x
		//row_idx = y
		//Kontrolli kas grid[x] on olemas. Kui ei, siis pane sinna {}
		//Siis sellest eelnevast sõltuvalt tee ekraanile element ja lisa dictionarysse lahter nii:
		/*
		grid[col_idx][row_idx] = {
			el: blah,
			true_val: val
		}
		*/
	})
})

//Sul peaks nüüd olema grid. Selle põhjal on vaja ehitada mingi ekraanile minev asi.
//Olen hoolitsenud, et func.js on saadaval, nii et f.addElement töötab.
//Vaja joonistada ekraanile algne versioon sudokust.
//Kui see on tehtud siis saad tegeleda sellega, et lahtritesse saaks kirjutada jne.
//Üks kriitiline asi on, et koodis olevas tabelis oleks ekraanil olevatele lahtritele viited.
//A la, et saad lihtsalt teha
//grid[0][4].div ja saad kätte ekraanil oleva elemendi, et selle väärtus lugeda näiteks.

//Kontrollimiseks soovitan lisada eraldi nupu.
//Sudoku reegel: samas reas ega veerus ei tohi numbrid korduda.
//Loopimiseks soovitan kasutada tavalist for-tsüklit
//Hea on kontrollida täitsa eraldi kordadega.

for(let x=0;x<puzzle.size;x++){
	var seen = []
	for(let y=0;y<puzzle.size;y++){
		
	}
}