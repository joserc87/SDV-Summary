import time
from flask import Blueprint, render_template, request, g, flash, session
from uploadfarm import connect_db
from uploadfarm.blueprints.blog import get_blogposts

admin = Blueprint('admin', __name__,
                  template_folder='templates')


@admin.route('/',methods=['GET','POST'])
def index():
    start_time = time.time()
    error = None
    if 'admin' in session:
        #trusted
        returned_blog_data = None
        g.db = connect_db()
        cur = g.db.cursor()
        if request.method == 'POST':
            if request.form['blog'] == 'Post':
                live = False
                if 'live' in request.form:
                    if request.form['live']=='on':
                        live = True
                if request.form['content'] == '' or request.form['blogtitle'] == '':
                    error = 'Failed to post blog entry, title or body was empty!'
                    returned_blog_data = {'blogtitle':request.form['blogtitle'],
                                            'content':request.form['content'],
                                            'checked': live}
                else:
                    cur.execute('INSERT INTO blog (time, author, title, post, live) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(int(time.time()),session['admin'],request.form['blogtitle'],request.form['content'],live))
                    g.db.commit()
                    if live == True:
                        flash('Posted blog entry "'+str(request.form['blogtitle']+'"'))
                    else:
                        flash('Saved unposted blog entry "'+str(request.form['blogtitle']+'"')) 
            elif request.form['blog'] == 'update':
                state = request.form['live'] == 'true'
                cur.execute('UPDATE blog SET live='+app.sqlesc+' WHERE id='+app.sqlesc,(state,request.form['id']))
                g.db.commit()
                return 'Success'
            elif request.form['blog'] == 'delete':
                cur.execute('DELETE FROM blog WHERE id='+app.sqlesc,(request.form['id'],))
                g.db.commit()
                return 'Success'
        cur.execute('SELECT url,name,farmName,date FROM playerinfo')
        entries = cur.fetchall()
        return render_template('adminpanel.html',returned_blog_data=returned_blog_data,blogposts=get_blogposts(include_hidden=True),entries=entries,error=error, processtime=round(time.time()-start_time,5))
    else:
        if request.method == 'POST':
            if 'blog' in request.form:
                return 'Failure'
            else:
                try:
                    g.db = connect_db()
                    cur = g.db.cursor()
                    cur.execute('SELECT password FROM admin WHERE username='+app.sqlesc+' ORDER BY id',(request.form['username'],))
                    r = cur.fetchone()
                    if r != None:
                        if check_password_hash(r[0],request.form['password']) == True:
                            session['admin']=request.form['username']
                            return redirect(url_for('admin_panel'))
                    cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),'failed login: '+request.form['username']))
                    g.db.commit()
                    g.db.close()
                    error = 'Incorrect username or password'
                except:
                    pass
        return render_template('admin.html',error=error,processtime=round(time.time()-start_time,5))
