import os,sys,tempfile,ctypes,traceback
from ctypes import wintypes

if os.name == "nt":
	FSCTL_FILE_FLUSH_AND_PURGE_CACHE = 0x900f3
	kernel32 = ctypes.windll.kernel32

	def _windows_full_flush(fd):
		handle = ctypes.c_void_p(fd)
		kernel32.FlushFileBuffers(handle)  # Best-effort
		bytes_returned = wintypes.DWORD()
		kernel32.DeviceIoControl(
			handle, FSCTL_FILE_FLUSH_AND_PURGE_CACHE,
			None, 0, None, 0, ctypes.byref(bytes_returned), None
		)

def write(path,data,mode="wb"):
	dirpath = os.path.dirname(path) or "."
	os.makedirs(dirpath,exist_ok=True)
	with open(path+"_temp",mode) as f:
		f.write(data)
		f.flush()
		os.fsync(f.fileno())
	os.replace(path+"_temp",path)
	if os.name != "nt":
		dir_fd = os.open(os.path.dirname(path), os.O_DIRECTORY)
		os.fsync(dir_fd)
		os.close(dir_fd)
def write_safe(filepath,data,mode="wb"):
	dirpath = os.path.dirname(filepath) or "."
	filename = os.path.basename(filepath)
	
	os.makedirs(dirpath,exist_ok=True)

	temp_fd = None
	temp_path = None
	try:
		with tempfile.NamedTemporaryFile(
			mode=mode,
			prefix=f".{filename}.tmp.",
			dir=dirpath,
			delete=False
		) as tf:
			temp_path = tf.name
			temp_fd = tf.fileno()

			tf.write(data)
			tf.flush()

			if os.name == "nt":
				_windows_full_flush(temp_fd)
			else:
				os.fsync(temp_fd)

		if os.name == "nt":
			# Preferred: ReplaceFileW (atomic, preserves some attrs)
			success = ctypes.windll.kernel32.ReplaceFileW(
				str(filepath), str(temp_path), None, 0, None, None
			)
			if not success:
				err = ctypes.get_last_error()
				# Fallback to MoveFileEx
				flags = 1 | 8  # REPLACE_EXISTING | WRITE_THROUGH
				success = ctypes.windll.kernel32.MoveFileExW(
					str(temp_path), str(filepath), flags
				)
				if not success:
					raise OSError(err or ctypes.get_last_error(), f"Windows atomic replace failed (ReplaceFile error {err})")
		else:
			os.replace(temp_path, filepath)

	except Exception:
		# Only cleanup temp on failure
		if temp_path and os.path.exists(temp_path):
			try:
				os.unlink(temp_path)
			except OSError:
				pass
		raise

# try:
	# write_safe("my_important_file.txt", b"Safe content here")
	# print("Success: File created safely as 'my_important_file.txt'")
# except Exception as e:
	# print("Failed:", e)
	# import traceback
	# traceback.print_exc()