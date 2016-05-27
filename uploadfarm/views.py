import time
import io
import hashlib
import defusedxml
import json
import random
import sqlite3
import psycopg2
import os
from xml.etree.ElementTree import ParseError
from flask import render_template, jsonify, g, request, session, redirect, url_for
from uploadfarm import app
from uploadfarm import connect_db
from uploadfarm.savehandling.savefile import savefile
from uploadfarm.savehandling.playerInfo import playerInfo
from uploadfarm.savehandling.farmInfo import getFarmInfo
from uploadfarm.tools.bigbase import dec2big
from uploadfarm.blueprints.blog import get_blogposts
from werkzeug import secure_filename, check_password_hash
from werkzeug.security import generate_password_hash
from uploadfarm.imagegeneration.imageDrone import process_queue

def get_logged_in_user():
    if logged_in():
        return session['logged_in_user'][0]
    else:
        return None


def logged_in():
    # designed to prevent repeated db requests
    if not hasattr(g, 'logged_in_user'):
        if 'logged_in_user' in session:
            g.db = connect_db()
            cur = g.db.cursor()
            cur.execute('SELECT auth_key FROM users WHERE id='+app.sqlesc,(session['logged_in_user'][0],))
            result = cur.fetchall()
            if len(result) == 0:
                session.pop('logged_in_user',None)
                g.logged_in_user = False
            elif result[0][0] == session['logged_in_user'][1]:
                g.logged_in_user = True
            else:
                session.pop('logged_in_user',None)
                g.logged_in_user = False
        else:
            g.logged_in_user = False
    return g.logged_in_user

app.jinja_env.globals.update(logged_in=logged_in)
app.jinja_env.globals.update(list=list)
app.jinja_env.add_extension('jinja2.ext.do')


def add_to_series(rowid, uniqueIDForThisGame, name, farmName):
    current_auto_key = json.dumps([uniqueIDForThisGame, name, farmName])
    db = connect_db()
    cur = db.cursor()
    if logged_in():
        logged_in_userid = session['logged_in_user'][0]
        cur.execute('SELECT id, owner, members_json FROM series WHERE auto_key_json='+app.sqlesc+' AND owner='+app.sqlesc,(current_auto_key,logged_in_userid))
        result = cur.fetchall()
        db.commit()
        assert len(result)<= 1
        if len(result)==0:
            cur.execute('INSERT INTO series (owner, members_json, auto_key_json) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+') RETURNING id',(logged_in_userid,json.dumps([rowid]),current_auto_key))
            series_id = cur.fetchall()[0][0]
        elif len(result)==1:
            series_id = result[0][0]
            new_members_json = json.dumps(json.loads(result[0][2])+[rowid])
            cur.execute('UPDATE series SET members_json='+app.sqlesc+' WHERE id='+app.sqlesc,(new_members_json,result[0][0]))
    else:
        cur.execute('INSERT INTO series (members_json, auto_key_json) VALUES ('+app.sqlesc+','+app.sqlesc+') RETURNING id',(json.dumps([rowid]),current_auto_key))
        series_id = cur.fetchall()[0][0]
    db.commit()
    db.close()
    return series_id


def md5(md5file):
    h = hashlib.md5()
    if type(md5file) == io.BytesIO:
        h.update(md5file.getvalue())
    else:
        for chunk in iter(lambda: md5file.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


@app.route('/faq')
def faq():
    error = None
    start_time=time.time()
    return render_template('faq.html',error=error,processtime=round(time.time()-start_time,5))


def get_entries(n=6,**kwargs):
    '''
    Returns n entries; has kwargs:
        include_failed  bool    if True includes uploads which failed image generation
        search_terms    text    search string
        series          text    takes 'url' as key; finds all matching in series    
        offset          int     to allow for pagination
        sort_by         text    'rating', 'views', 'recent'; 'rating' defined according to snippet from http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
    '''
    order_types = {'rating':'ORDER BY ((positive_votes + 1.9208) / (positive_votes + negative_votes) - 1.96 * SQRT((positive_votes*negative_votes)/(positive_votes+negative_votes)+0.9604) / (positive_votes+negative_votes)) / ( 1 + 3.8416 / (positive_votes + negative_votes)) ',
                    'views':'ORDER BY views ',
                    'recent':'ORDER BY id '}
    search_fields = ('name','farmName')
    g.db = connect_db()
    cur = g.db.cursor()
    where_contents = []
    if 'include_failed' not in kwargs or 'include_failed' in kwargs and kwargs['include_failed'] == False:
        where_contents.append('failed_processing IS NOT TRUE')
    if 'sort_by' in kwargs and kwargs['sort_by'] == 'rating':
        where_contents.append('positive_votes + negative_votes > 0')
    if 'search_terms' in kwargs and len(kwargs['search_terms'])>0:
        search = ''
        for i, item in enumerate(kwargs['search_terms']):
            if i == 0:
                search+='('
            else:
                search+='AND '
            for f, field in enumerate(search_fields):
                if f == 0:
                    search+='('
                else:
                    search+='OR '
                print('testing...')
                search+=cur.mogrify(field +' ILIKE '+app.sqlesc+' ',('%%'+item.decode('utf-8')+'%%',)).decode('utf-8')
                if f == len(search_fields)-1:
                    search+=')'
            if i == len(kwargs['search_terms'])-1:
                search+=')'
        where_contents.append(search)
    if 'series' in kwargs and kwargs['series']!=None:
        where_contents.append(cur.mogrify('series_id=(SELECT series_id FROM playerinfo WHERE url='+app.sqlesc+')',(kwargs['series'],)).decode('utf-8'))
    where = ''
    for c,contents in enumerate(where_contents):
        if c == 0:
            where+='WHERE '+contents+' '
        if c != 0:
            where+='AND '+contents+' '
    order = 'ORDER BY id ' if 'sort_by' not in kwargs else order_types[kwargs['sort_by']]
    query = 'SELECT url, name, farmName, date, avatar_url, farm_url FROM playerinfo '+where+order+'DESC LIMIT '+app.sqlesc
    print('query:',query)
    offset = 0
    # print(query)
    if 'offset' in kwargs:
        offset = kwargs['offset']
        query += " OFFSET "+app.sqlesc
    if 'offset' in kwargs:
        cur.execute(query,(n,offset))
    else:
        cur.execute(query,(n,))
    entries = {}
    entries['posts'] = cur.fetchall()
    cur.execute('SELECT count(*) FROM playerinfo '+where)
    entries['total'] = cur.fetchone()[0]
    if len(entries)==0:
        entries == None
    g.db.close()
    return entries



@app.route('/lo')
def logout():
    if 'admin' in session:
        session.pop('admin',None)
    session.pop('logged_in_user',None)
    return redirect(url_for('home'))


@app.route('/all')
def allmain():
    error = None
    start_time = time.time()
    num_entries = 18
    #print(request.args.get('p'))
    arguments = {'include_failed':True}
    try:
        arguments['offset'] = int(request.args.get('p')) * num_entries
    except TypeError:
        arguments['offset'] = 0
    except:
        error = "No browse with that ID!"
        return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))
    if arguments['offset'] < 0:
        return redirect(url_for('allmain'))
    #adapt get_recents() to take a kwarg for sort type; sort type can be GET value: /all&sort=popular
    arguments['sort_by'] = request.args.get('sort') if request.args.get('sort') != None else 'recent'
    if 'series' in request.args:
        arguments['series'] = request.args.get('series')
    if 'search' in request.args:
        arguments['search_terms'] = [item.encode('utf-8') for item in request.args.get('search').split(' ')[:10]]
    # try:
    entries = get_entries(num_entries,**arguments)
    # except:
    #   error = 'Malformed request for entries!'
    #   return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))
    if entries['total']<=arguments['offset'] and entries['total']>0:
        return redirect(url_for('allmain'))
    return render_template('all.html',full=True,offset=arguments['offset'],recents=entries,error=error, processtime=round(time.time()-start_time,5))


def is_duplicate(md5_info,player_info):
    db = connect_db()
    cur = db.cursor()
    cur.execute('SELECT id, md5, name, uniqueIDForThisGame, url, del_token FROM playerinfo WHERE md5='+app.sqlesc,(md5_info,))
    matches = cur.fetchall()
    if len(matches) > 0:
        for match in matches:
            if str(player_info['name'])==str(match[2]) and str(player_info['uniqueIDForThisGame'])==str(match[3]):
                db.close()
                return (match[4],match[5])
        db.close()
        return False
    else:
        db.close()
        return False


def insert_info(player_info,farm_info,md5_info):
    columns = []
    values = []
    # player_info['date'] = ['Spring','Summer','Autumn','Winter'][int(((player_info['stats']['DaysPlayed']%(28*4))-((player_info['stats']['DaysPlayed']%(28*4))%(28)))/28)]+' '+str((player_info['stats']['DaysPlayed']%(28*4))%(28))+', Year '+str(((player_info['stats']['DaysPlayed']-player_info['stats']['DaysPlayed']%(28*4))/(28*4))+1)
    for key in player_info.keys():
        if type(player_info[key]) == list:
            for i,item in enumerate(player_info[key]):
                columns.append(key.replace(' ','_') + str(i))
                values.append(str(item))
        elif type(player_info[key]) == dict:
            for subkey in player_info[key]:
                if type(player_info[key][subkey]) == dict:
                    for subsubkey in player_info[key][subkey]:
                        columns.append((key+subkey+subsubkey).replace(' ','_'))
                        values.append((player_info[key][subkey][subsubkey]))
                else:
                    columns.append((key + subkey).replace(' ','_'))
                    values.append(str(player_info[key][subkey]))
        else:
            columns.append(key)
            values.append(str(player_info[key]))
    columns.append('farm_info')
    values.append(json.dumps(farm_info))
    columns.append('added_time')
    values.append(time.time())
    columns.append('md5')
    values.append(md5_info)
    columns.append('ip')
    values.append(request.environ['REMOTE_ADDR'])
    columns.append('del_token')
    del_token = random.randint(-(2**63)-1,(2**63)-1)
    values.append(del_token)
    columns.append('views')
    values.append('0')
    default_images = [['avatar_url','static/placeholders/avatar.png'],
                      ['farm_url','static/placeholders/minimap.png'],
                      ['map_url','static/placeholders/'+str(player_info['currentSeason'])+'.png'],
                      ['portrait_url','static/placeholders/portrait.png']]
    for default in default_images:
        columns.append(default[0])
        values.append(default[1])

    colstring = ''
    for c in columns:
        colstring += c+', '
    colstring = colstring[:-2]
    questionmarks = ((app.sqlesc+',')*len(values))[:-1]
    g.db = connect_db()
    cur = g.db.cursor()
    try:
        cur.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+') RETURNING id,added_time',tuple(values))
        row = cur.fetchone()
        url = dec2big(int(row[0])+int(row[1]))
        rowid = row[0]
        cur.execute('UPDATE playerinfo SET url='+app.sqlesc+' WHERE id='+app.sqlesc+'',(url,rowid))
        cur.execute('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',('process_image',rowid))
        g.db.commit()
        return url, del_token, rowid, None
    except (sqlite3.OperationalError, psycopg2.ProgrammingError) as e:
        g.db.rollback()
        cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),str(e)+' '+json.dumps([columns,values])))
        g.db.commit()
        return False, del_token, False, "Save file incompatible with current database: error is "+str(e)


def file_uploaded(inputfile):
    memfile = io.BytesIO()
    inputfile.save(memfile)
    md5_info = md5(memfile)
    try:
        save = savefile(memfile.getvalue(), True)
        player_info = playerInfo(save)
    except defusedxml.common.EntitiesForbidden:
        error = "I don't think that's very funny"
        return {'type':'render','target':'index.html','parameters':{"error":error}}
    except IOError:
        error = "Savegame failed sanity check (if you think this is in error please let us know)"
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),'failed sanity check '+str(secure_filename(inputfile.filename))))
        g.db.commit()
        g.db.close()
        return {'type': 'render', 'target': 'index.html', 'parameters': {"error": error}}
    except AttributeError as e:
        error = "Not valid save file - did you select file 'SaveGameInfo' instead of 'playername_number'?"
        print(e)
        return {'type': 'render', 'target': 'index.html', 'parameters': {"error": error}}
    except ParseError as e:
        error = "Not well-formed xml"
        return {'type':'render','target':'index.html','parameters':{"error":error}}
    dupe = is_duplicate(md5_info,player_info)
    if dupe != False:
        session[dupe[0]] = md5_info
        session[dupe[0]+'del_token'] = dupe[1]
        return {'type':'redirect','target':'profile.display_data','parameters':{"url":dupe[0]}}
        return redirect(url_for('profile.display_data',url=dupe[0]))
    else:
        farm_info = getFarmInfo(save)
        outcome, del_token, rowid, error = insert_info(player_info,farm_info,md5_info)
        if outcome != False:
            filename = os.path.join(app.config['UPLOAD_FOLDER'],outcome)
            with open(filename,'wb') as f:
                f.write(memfile.getvalue())
            series_id = add_to_series(rowid,player_info['uniqueIDForThisGame'],player_info['name'],player_info['farmName'])
            owner_id = get_logged_in_user()
            g.db = connect_db()
            cur = g.db.cursor()
            cur.execute('UPDATE playerinfo SET savefileLocation='+app.sqlesc+', series_id='+app.sqlesc+', owner_id='+app.sqlesc+' WHERE url='+app.sqlesc+';',(filename,series_id,owner_id,outcome))
            g.db.commit()
            g.db.close()
        else:
            if error == None:
                error = "Error occurred inserting information into the database!"
            return {'type':'render','target':'index.html','parameters':{"error":error}}
        process_queue()
        memfile.close()
    if outcome != False:
        session.permanent = True
        session[outcome] = md5_info
        session[outcome+'del_token'] = del_token
        return {'type':'redirect','target':'profile.display_data','parameters':{"url":outcome}}



def get_recents(n=6,**kwargs):
    g.db = connect_db()
    cur = g.db.cursor()
    recents = {}
    where = 'WHERE failed_processing IS NOT TRUE '
    if 'include_failed' in kwargs:
        if kwargs['include_failed']==True:
            where = ''
    query = 'SELECT url, name, farmName, date, avatar_url, farm_url FROM playerinfo '+where+'ORDER BY id DESC LIMIT '+app.sqlesc
    offset = 0
    if 'offset' in kwargs:
        offset = kwargs['offset']
        query += " OFFSET "+app.sqlesc
    if 'offset' in kwargs:
        cur.execute(query,(n,offset))
    else:
        cur.execute(query,(n,))
    recents['posts'] = cur.fetchall()
    cur.execute('SELECT count(*) FROM playerinfo')
    recents['total'] = cur.fetchone()[0]
    if len(recents)==0:
        recents == None
    g.db.close()
    return recents


@app.route('/',methods=['GET','POST'])
def home():
    start_time = time.time()
    error = None
    if request.method == 'POST':
        inputfile = request.files['file']
        if inputfile:
            result = file_uploaded(inputfile)
            if result['type'] == 'redirect':
                return redirect(url_for(result['target'],**result['parameters']))
            elif result['type'] == 'render':
                params = {'error':error,'blogposts':get_blogposts(5),'recents':get_recents(),'processtime':round(time.time()-start_time,5)}
                if 'parameters' in result:
                    for key in result['parameters'].keys():
                        params[key] = result['parameters'][key]
                return render_template(result['target'], **params)
    return render_template("index.html", recents=get_recents(), error=error,blogposts=get_blogposts(5), processtime=round(time.time()-start_time,5))


@app.route('/_get_recents')
def jsonifyRecents():
    return jsonify(recents=get_recents()['posts'])


@app.route('/login', methods=['GET','POST'])
def login():
    start_time = time.time()
    error = None
    session.permanent = True
    if 'logged_in_user' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
            error = 'Missing email or password for login!'
        else:
            time.sleep(0.2)
            g.db = connect_db()
            cur = g.db.cursor()
            cur.execute('SELECT id,password,auth_key FROM users WHERE email='+app.sqlesc,(request.form['email'],))
            result = cur.fetchall()
            assert len(result) <= 1
            if len(result) == 0:
                error = 'Username not found!'
            else:
                if check_password_hash(result[0][1], request.form['password']) is True:
                    if result[0][2] is None:
                        auth_key = dec2big(random.randint(0,(2**128)))
                        cur.execute('UPDATE users SET auth_key='+app.sqlesc+', login_time='+app.sqlesc+' WHERE id='+app.sqlesc,(auth_key,time.time(),result[0][0]))
                        g.db.commit()
                    else:
                        auth_key = result[0][2]
                    session['logged_in_user']=(result[0][0],auth_key)
                    return redirect(url_for('home'))
                else:
                    error = 'Incorrect password!'
    return render_template("login.html",error=error,processtime=round(time.time()-start_time,5))


@app.route('/su',methods=['GET','POST'])
def signup():
    start_time = time.time()
    error=None
    if 'logged_in_user' in session:
        error = 'You are already logged in!'
    elif request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
            error = 'Missing email or password!'
        elif len(request.form['password'])<app.config['PASSWORD_MIN_LENGTH']:
            error = 'Password too short!'
        else:
            if recaptcha.verify():
                g.db = connect_db()
                cur = g.db.cursor()
                cur.execute('SELECT id FROM users WHERE email='+app.sqlesc,(request.form['email'],))
                result = cur.fetchall()
                if len(result) == 0:
                    if len(request.form['email'].split('@')) == 2 and len(request.form['email'].split('@')[1].split('.'))>= 2:
                        cur.execute('INSERT INTO users (email,password) VALUES ('+app.sqlesc+','+app.sqlesc+')',(request.form['email'],generate_password_hash(request.form['password'])))
                        g.db.commit()
                        flash('You have successfully registered. Now, please sign in!')
                        return redirect(url_for('login'))
                    else:
                        error = 'Invalid email address!'
                else:
                    error = 'This email address has already registered'
            else:
                error = 'Captcha failed! If you are human, please try again!'
    return render_template("signup.html",error=error,processtime=round(time.time()-start_time,5))
