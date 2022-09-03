var table = {
	dogs: "yes",
	cats: 5
}
var jmsg = JSON.stringify(table)
var req = new XMLHttpRequest()
req.open("POST",window.location.href,true)
req.send(jmsg)
