function blog_open(){
	//f.send("blog-post-get",{"idx":0})
	fetch("blog/posts/0.md")
	.then(resp=>resp.text())
	.then(data=>{
		data = data.replaceAll("\n","<br>")
		window.blog_entries.innerHTML = data
		console.log(data)
	})
}
function blog_message(msg){
	//window.blog_entries
	console.log(msg)
}
f.view.register("blog",blog_open,blog_message)
