from flask import Flask, render_template, redirect, url_for, request, flash
import time
import config
from werkzeug import secure_filename
import os
from playerInfo import playerInfo

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

@app.route('/',methods=['GET','POST'])
def home():
	start_time = time.time()
	error = None
	if request.method == 'POST':
		inputfile = request.files['file']
		if inputfile:
			filename = secure_filename(inputfile.filename)
			inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			player_info = playerInfo(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			error = str(player_info)
			#note to self: need to have better handling for this, this is just a stop-gap!
	return render_template("index.html", error=error, processtime=round(time.time()-start_time,5))

@app.route('/upload',methods=['GET','POST'])
def upload():
	return 'wat'



if __name__ == "__main__":
	app.run(debug=True)