from flask import Flask, render_template, redirect, url_for, request, flash
import time
import config
from werkzeug import secure_filename
import os
from playerInfo import playerInfo
from farmInfo import getFarmInfo

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024


import hashlib 
def md5(inputfile):
	h = hashlib.md5()
	for chunk in iter(lambda: inputfile.read(4096), b""):
		h.update(chunk)
	return h.hexdigest()


@app.route('/',methods=['GET','POST'])
def home():
	start_time = time.time()
	error = None
	if request.method == 'POST':
		inputfile = request.files['file']
		if inputfile:
			filename = secure_filename(inputfile.filename)
			inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			upload_md5 = md5(inputfile)
			player_info = playerInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			farm_info = getFarmInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			error = str(upload_md5)
			#note to self: need to have better handling for this, this is just a stop-gap!
	return render_template("index.html", error=error, processtime=round(time.time()-start_time,5))

@app.route('/upload',methods=['GET','POST'])
def upload():
	return 'wat'



if __name__ == "__main__":
	app.run(debug=True)