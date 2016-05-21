import time
import datetime
from flask import Blueprint, render_template, g
from flask import current_app as app
from uploadfarm import connect_db

blog = Blueprint('blog', __name__,
                 template_folder='templates')


def get_blogposts(n=False,**kwargs):
    g.db = connect_db()
    cur = g.db.cursor()
    blogposts = None
    query = "SELECT id,time,author,title,post,live FROM blog"
    metaquery = "SELECT count(*) FROM blog"
    try:
        if kwargs['include_hidden'] == False:
            query += " WHERE live='1'"
            metaquery += " WHERE live='1'"
    except KeyError:
        query += " WHERE live='1'"
        metaquery += " WHERE live='1'"
    query += " ORDER BY id DESC"
    if app.config['USE_SQLITE'] == True:
        if n==False:
            n=-1
    if n!=False:
        query += " LIMIT "+app.sqlesc
    offset = 0
    if 'offset' in kwargs:
        offset = kwargs['offset']
    query += " OFFSET "+app.sqlesc
    if n==False:
        cur.execute(query,(offset,))
    else:
        cur.execute(query,(n,offset))
    blogposts = list(cur.fetchall())
    for b,blogentry in enumerate(blogposts):
        blogposts[b] = list(blogentry)
        blogposts[b][1] = datetime.datetime.fromtimestamp(blogentry[1])
    cur.execute(metaquery)
    metadata = cur.fetchone()
    blogdict = {'total':metadata[0],
                'posts':blogposts}
    return blogdict


@blog.route('/')
def index():
    error = None
    start_time = time.time()
    num_entries = 5
    try:
        offset = int(request.args.get('p')) * num_entries
    except:
        offset = 0
    if offset < 0:
        return redirect(url_for('blogmain'))
    blogposts = get_blogposts(num_entries, offset=offset)
    if blogposts['total'] <= offset and blogposts['total'] > 0:
        return redirect(url_for('blogmain'))
    return render_template('blog.html', full=True, offset=offset, blogposts=blogposts, error=error, processtime=round(time.time()-start_time, 5))


@blog.route('/<id>')
def post(id):
    error = None
    start_time = time.time()
    try:
        blogid = int(id)
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute("SELECT id,time,author,title,post,live FROM blog WHERE id="+app.sqlesc+" AND live='1'",(blogid,))
        blogdata = cur.fetchone()
        if blogdata is not None:
            blogdata = list(blogdata)
            blogdata[1] = datetime.datetime.fromtimestamp(blogdata[1])
            blogposts = {'posts':(blogdata,),'total':1}
            return render_template('blog.html',full=True,offset=0,blogposts=blogposts,error=error, processtime=round(time.time()-start_time,5))
        else:
            error = "No blog with ID: {}".format(blogid)
    except Exception as e:
        print(e)
        error = "No blog with ID: {}".format(id)
    return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))