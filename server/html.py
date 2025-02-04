from html.parser import HTMLParser
from server import io
def load(path):
	data = io.get_file_data(path,"r")
	
	return data.encode("utf-8")
	

from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.modified_html = ''

	def handle_starttag(self, tag, attrs):
		self.modified_html += f"<{tag}{' ' + ' '.join(f'{k}=\"{v}\"' for k, v in attrs) if attrs else ''}>"

	def handle_endtag(self, tag):
		self.modified_html += f"</{tag}>"

	def handle_data(self, data):
		# Replace 'Old Title' with 'New Title'
		self.modified_html += data.replace('Old Title', 'New Title')

html = '<html><body><h1>Old Title</h1></body></html>'
parser = MyHTMLParser()
parser.feed(html)

print(parser.modified_html)