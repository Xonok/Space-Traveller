function blog_open(){
	//net.post_json({command:"blog-post-get",idx:0})
	fetch("blog/posts/0.md")
	.then(resp=>resp.text())
	.then(data=>{
		data = data.replaceAll("\n","<br>")
		window.blog_entries.innerHTML = data
		console.log(data)
	})
}
blog_open()
