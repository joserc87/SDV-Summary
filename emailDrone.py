import json
from flask import Flask
from flask_mail import Mail, Message
from app import app, connect_db
import uuid
import time

sqlesc = app.sqlesc
mail = Mail(app)

def email_confirmation(address,user_id,key):
	title = 'Confirm upload.farm registration'
	body = 'Hello! You have signed up for an account on upload.farm. To verify your email address, please visit: http://upload.farm/verify_email?i='+str(user_id)+'&t='+str(key)
	html = '<p>Hello! You have signed up for an account on upload.farm. To verify your email address, please <a href="http://upload.farm/verify_email?i='+str(user_id)+'&t='+str(key)+'">click here</a>. Thanks!</p>'
	send_email(address,title,body,html)

def email_passwordreset():
	pass

def send_email(address, title, body, html):
	with app.app_context():
		msg = Message(title,recipients=[address])
		msg.body = body
		msg.html = html
		mail.send(msg)

def process_email():
	start_time = time.time()
	records_handled = 0
	db = connect_db()
	cur = db.cursor()
	while True:
		cur.execute('UPDATE todo SET currently_processing='+sqlesc+' WHERE id=(SELECT id FROM todo WHERE task='+sqlesc+' AND currently_processing IS NOT TRUE LIMIT 1) RETURNING *',(True,'email_confirmation',))
		tasks = cur.fetchall()
		db.commit()
		# print tasks
		if len(tasks) != 0:
			for task in tasks:
				cur.execute('UPDATE users SET email_conf_token=(CASE WHEN email_conf_token IS NULL THEN '+sqlesc+' WHEN email_conf_token IS NOT NULL THEN email_conf_token END) WHERE id='+sqlesc+' RETURNING email, id, email_conf_token',(str(uuid.uuid4()),task[2]))
				email_data = cur.fetchall()[0]
				email_confirmation(*email_data)
				cur.execute('DELETE FROM todo WHERE id=('+sqlesc+')',(task[0],))
				db.commit()
				records_handled += 1
		else:
			db.close()
			return time.time()-start_time, records_handled

if __name__ == "__main__":
	print(process_email())
