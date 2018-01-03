from multiprocessing import Process
from flask import Flask, request, redirect
from database import set_user_info
from config import server_location


def launch_webserver_as_process():
	p = Process(target=run_flask)
	p.start()
	return p

app = Flask(__name__)
def run_flask():
	app.run(port=6752)
	
@app.route("/pingback",methods=['GET'])
def home():
	info = {key:value for key, value in request.args.items()}
	info['invalidated_refresh_token'] = False
	set_user_info(info)
	return redirect(server_location)


if __name__ == "__main__":
	launch_webserver_as_process()
	# run_flask() # works on mac; maybe process doesnt?