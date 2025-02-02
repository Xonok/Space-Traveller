from server import io
def load(path):
	data = io.get_file_data(path)
	return data