import zipfile
import os

def zopen(filename):
	'''
	designed to replace open() for zipped savegames
	'''
	try:
		file = _zopen(filename)
	except zipfile.BadZipfile:
		with open(filename,'r') as f:
			data = f.read()
		zwrite(data,filename)
		file = _zopen(filename)
	return file

def _zopen(filename):
	'''
	internal, no-fuss opening of zipfile
	'''
	# filename = os.path.splitext(filename)[0]
	zf = zipfile.ZipFile(filename,'r')
	file = zf.open(os.path.split(filename)[1],'r')
	zf.close()
	return file

def zwrite(data,filename):
	'''
	designed to replace saving unzipped savegames
	'''
	zf = zipfile.ZipFile(filename,'w',compression=zipfile.ZIP_DEFLATED)
	if type(data) not in [str,bytes]:
		data = data.read()
	zf.writestr(os.path.split(filename)[1],data,zipfile.ZIP_DEFLATED)
	zf.close()
	return


def main():
	import app
	upload_folder = app.app.config['UPLOAD_FOLDER']
	files = ['1AWerA','1AWerH','1AWeri','1AWerO','1AWerZ','1AWes9','1AXGWQ','1AXHfd','1AXIgW','1AXIiB','1B0WjE','1B0Y4H']
	for file in files:
		zopen(os.path.join(upload_folder,file))

if __name__=="__main__":
	main()