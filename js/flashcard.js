f.init()


var collection = {
	"hiragana": {
		"cards": [
			["あ", "a"],
			["か", "ka"],
			["さ", "sa"],
			["た", "ta"],
			["な", "na"],
			["は", "ha"],
			["や", "ya"],
			["ら", "chi"],
			["わ", "wa"],
			
			["い", "i"],
			["き", "ki"],
			["し", "shi"],
			["ち", "chi"],
			["に", "ni"],
			["ひ", "hi"],
			["み", "mi"],
			["り", "ri"],
			
			["う", "u"],
			["く", "ku"],
			["す", "su"],
			["つ", "tsu"],
			["ぬ", "nu"],
			["ふ", "fu"],
			["む", "mu"],
			["ゆ", "yu"],
			["る", "ru"],
			["を", "wo"],
			
			["け", "ke"],
			["せ", "se"],
			["て", "te"],
			["ね", "ne"],
			["へ", "he"],
			["ね", "ne"],
			["れ", "re"],
			
			["こ", "ko"],
			["そ", "so"],
			["と", "to"],
			["の", "no"],
			["ほ", "ho"],
			["も", "mo"],
			["よ", "yo"],
			["ろ", "ro"],
			["ん", "n,(nn)"],
			
			["が", "ga"],
			["ざ", "za"],
			["だ", "da"],
			["ば", "ba"],
			["ぱ", "pa"],
			
			["ぎ", "gi"],
			["じ", "ji"],
			["ぢ", "dzi, (di)"],
			["び", "bi"],
			["ぴ", "pi"],
			
			["ぐ", "gu"],
			["ず", "zu"],
			["づ", "dzu,(du)"],
			["ぶ", "bu"],
			["ぷ", "pu"],
			
			["げ", "ge"],
			["ぜ", "ze"],
			["で", "de"],
			["べ", "be"],
			["ぺ", "pe"],
			
			["ご", "go"],
			["ぞ", "zo"],
			["ど", "do"],
			["ぼ", "bo"],
			["ぽ", "po"],
			
			["きゃ", "kya"],
			["しゃ", "sha"],
			["ちゃ", "cha"],
			["にゃ", "nya"],
			["ひゃ", "hya"],
			["みゃ", "mya"],
			["りゃ", "rya"],
			["ぎゃ", "gya"],
			["じゃ", "ja"],
			["ぢゃ", "dja, (da)"],
			["びゃ", "bya"],
			["ぴゃ", "pya"],
			
			["きゅ", "kyu"],
			["しゅ", "shu"],
			["ちゅ", "chu"],
			["にゅ", "nyu"],
			["ひゅ", "hyu"],
			["みゅ", "myu"],
			["りゅ", "ryu"],
			["ぎゅ", "gyu"],
			["じゅ", "ju"],
			["ぢゅ", "dju, (du)"],
			["ひゅ", "hyu"],
			["ぴゅ", "pyu"],
			
			["きょ", "kyo"],
			["しょ", "sho"],
			["ちょ", "cho"],
			["にょ", "nyo"],
			["ひょ", "hyo"],
			["みょ", "myo"],
			["りょ", "ryo"],
			["ぎょ", "gyo"],
			["じょ", "jo"],
			["ぢょ", "djo, (do)"],
			["ひょ", "byo"],
			["ぴょ", "pyo"]
		]
	}
}

// collection.hiragana.forEach((front,back)=>{})

var len = collection.hiragana.cards.length
function random_card(){
	var idx = Math.floor(Math.random()*len)
	var entry = collection.hiragana.cards[idx]
	console.log(entry)
	window.fc_front.style.display = null
	window.fc_back.style.display = "none"
	window.fc_front.innerHTML = "Question:<br>"+entry[0]
	window.fc_back.innerHTML = "Answer:<br>"+entry[1]
	window.fc_front.onclick = e=>{
		window.fc_front.style.display = "none"
		window.fc_back.style.display = null
		window.fc_good.style.display = null
		window.fc_bad.style.display = null
	}
	window.fc_back.onclick = e=>{
		window.fc_back.style.display = "none"
		window.fc_front.style.display = null
		window.fc_good.style.display = "none"
		window.fc_bad.style.display = "none"
	}
	window.fc_good.style.display = "none"
	window.fc_bad.style.display = "none"
	window.fc_good.onclick = random_card
	window.fc_bad.onclick = random_card
}
random_card()

//tinycards