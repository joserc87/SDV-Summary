import json
from app import app, connect_db

def check_email_verification():
	db = connect_db()
	cur = db.cursor()
	cur.execute('SELECT users.id FROM users WHERE users.email_confirmed IS NULL AND users.email_conf_token IS NULL AND NOT EXISTS (SELECT todo.id FROM todo WHERE todo.playerid=CAST(users.id AS text))')
	# cur.execute("SELECT users.id FROM (users INNER JOIN todo ON CAST(users.id AS text) != todo.playerid AND todo.task = 'email_confirmation') WHERE users.email_confirmed IS NULL AND users.email_conf_token IS NULL")
	user_ids = cur.fetchall()
	cur.executemany('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',[('old_email_confirmation',user_id[0]) for user_id in user_ids])
	db.commit()
	return len(user_ids)

def check_voting_base():
	db = connect_db()
	cur = db.cursor()
	cur.execute("SELECT id FROM playerinfo WHERE (positive_votes IS NULL OR positive_votes = 0) AND (negative_votes IS NULL OR negative_votes = 0)")
	player_ids = cur.fetchall()
	cur.executemany('UPDATE playerinfo SET positive_votes=1, negative_votes=1 WHERE id='+app.sqlesc,player_ids)
	db.commit()
	return len(player_ids)


def main():
	print('rebalanced the votes of {} playerinfo entries'.format(check_voting_base()))
	print('added {} accounts to email queue: if this is more than zero, you might need to manually run emailDrone'.format(check_email_verification()))

if __name__ == '__main__':
	main()