#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, request, flash, g, jsonify, make_response, send_from_directory, abort
from uploadfarm.config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
if app.config['USE_SQLITE'] == True:
    app.database = app.config['DB_SQLITE']
    app.sqlesc = '?'

    def connect_db():
        return sqlite3.connect(app.database)
else:
    app.database = 'dbname='+app.config['DB_NAME']+' user='+app.config['DB_USER']+' password='+app.config['DB_PASSWORD']
    app.sqlesc = '%s'

    def connect_db():
        return psycopg2.connect(app.database)

import time
from werkzeug import secure_filename, check_password_hash
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.security import generate_password_hash
import os
import sys
from uploadfarm.playerInfo import playerInfo
from uploadfarm.farmInfo import getFarmInfo
from uploadfarm.tools.bigbase import dec2big
import uploadfarm.generateSavegame
import json
import hashlib
from uploadfarm.imageDrone import process_queue
from uploadfarm.createdb import database_structure_dict, database_fields
import defusedxml
import operator
import random
import sqlite3
import psycopg2
import io
from xml.etree.ElementTree import ParseError
import datetime
from flask_recaptcha import ReCaptcha
import uuid
from google_measurement_protocol import Event, report
import uploadfarm.imgur
from uploadfarm.savefile import savefile

from uploadfarm.profile import profile
app.register_blueprint(profile)

if sys.version_info >= (3,0):
    unicode = str
else:
    str = unicode

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

recaptcha = ReCaptcha(app=app)
app.secret_key = app.config['SECRET_KEY']
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.wsgi_app = ProxyFix(app.wsgi_app)


def md5(md5file):
    h = hashlib.md5()
    if type(md5file) == io.BytesIO:
        h.update(md5file.getvalue())
    else:
        for chunk in iter(lambda: md5file.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

@app.route('/_get_recents')
def jsonifyRecents():
    return jsonify(recents=get_recents()['posts'])

@app.route('/login', methods=['GET','POST'])
def login():
    start_time=time.time()
    error=None
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
                if check_password_hash(result[0][1],request.form['password']) == True:
                    if result[0][2] == None:
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

@app.route('/acc',methods=['GET','POST'])
def account_page():
    start_time=time.time()
    error = None
    if not logged_in():
        error = 'You must be signed in to view your profile!'
        return render_template("login.html",error=error,processtime=round(time.time()-start_time,5))
    else:
        user = get_logged_in_user()
        claimables = find_claimables()
        g.db = connect_db()
        c = g.db.cursor()
        c.execute('SELECT id,auto_key_json FROM series WHERE owner='+app.sqlesc,(user,))
        r = c.fetchall()
        claimed_ids = {}
        for row in r:
            c.execute('SELECT url,date,imgur_json FROM playerinfo WHERE series_id='+app.sqlesc+' AND owner_id='+app.sqlesc,(row[0],user))
            s = c.fetchall()
            s = [list(part[:2])+[json.loads(part[2]) if part[2] != None else None] + list(part[3:]) for part in s]
            claimed_ids[row[0]] = {'auto_key_json':json.loads(row[1]),'data':s}
        claimable_ids = {}
        for row in claimables:
            c.execute('SELECT date FROM playerinfo WHERE id='+app.sqlesc,(row[0],))
            d = c.fetchone()[0]
            c.execute('SELECT auto_key_json FROM series WHERE id=(SELECT series_id FROM playerinfo WHERE id='+app.sqlesc+')',(row[0],))
            a = json.loads(c.fetchone()[0])
            claimable_ids[row[0]] = {'auto_key_json':a,'data':(row[1],d)}
        c.execute('SELECT email,imgur_json FROM users WHERE id='+app.sqlesc,(user,))
        e = c.fetchone()
        g.db.close()
        acc_info = {'email':e[0],'imgur':json.loads(e[1]) if e[1] != None else None}
        return render_template('account.html',error=error,claimed=claimed_ids,claimable=claimable_ids, acc_info=acc_info,processtime=round(time.time()-start_time,5))



def logged_in():
    # designed to prevent repeated db requests
    if not hasattr(g,'logged_in_user'):
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

def get_logged_in_user():
    if logged_in():
        return session['logged_in_user'][0]
    else:
        return None

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

@app.route('/_uploader',methods=['GET','POST'])
def api_upload():
    if request.method=='POST':
        if verify_api_auth(request.form):
            inputfile = request.files['file']
            result = file_uploaded(inputfile)
            analyticsEvent(uuid.uuid4(),'upload','automaticFileUpload')
            return jsonify(result)
        else:
            return abort(401)

def analyticsEvent(userid, category, action):
    event = Event(category,action)
    r = report(app.config['ANALYTICS_ID'],userid,event)
    return r

def verify_api_auth(form):
    if 'api_key' not in form or 'api_secret' not in form or form['api_key']=='':
        return False
    else:
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('SELECT id,api_secret,auth_key FROM users WHERE api_key='+app.sqlesc,(form['api_key'],))
        result = cur.fetchall()
        try:
            assert len(result) == 1
        except AssertionError:
            return False
        #if check_password_hash(result[0][1],form['api_secret']) == True:
        print('need to do proper storage of api keys (in another db table)...')
        if check_password_hash(form['api_secret'],result[0][1]) == True:
            if result[0][2] == None:
                auth_key = dec2big(random.randint(0,(2**128)))
                cur.execute('UPDATE users SET auth_key='+app.sqlesc+', login_time='+app.sqlesc+' WHERE id='+app.sqlesc,(auth_key,time.time(),result[0][0]))
                g.db.commit()
            else:
                auth_key = result[0][2]
            session['logged_in_user']=(result[0][0],auth_key)
            print('returning true')
            return True
        else:
            return False

@app.route('/_register-api',methods=['GET','POST'])
def api_register():
    if request.method=='POST':
        api_data = login_to_api(request.form)
        if api_data != False:
            analyticsEvent(uuid.uuid4(),'login','apiLogin')
            return api_data
        else:
            return abort(401)

def login_to_api(form):
    # takes username password, verifies they're in the db, if so, returns api key and hashed and salted password
    # either from db if exists, or generates them if not
    if 'email' not in form or 'password' not in form or form['email']=='':
        return False
    else:
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('SELECT id,password,api_key,api_secret FROM users WHERE email='+app.sqlesc,(form['email'],))
        result = cur.fetchall()
        try:
            assert len(result) == 1
        except AssertionError:
            return False
        #if check_password_hash(result[0][1],form['api_secret']) == True:
        if check_password_hash(result[0][1],form['password']) == True:
            if result[0][2] == None or result[0][3] == None:
                api_key = dec2big(random.randint(0,(2**128)))
                api_secret = dec2big(random.randint(0,(2**128)))
                cur.execute('UPDATE users SET api_key='+app.sqlesc+', api_secret='+app.sqlesc+' WHERE id='+app.sqlesc,(api_key,api_secret,result[0][0]))
                g.db.commit()
            else:
                api_key = result[0][2]
                api_secret = result[0][3]
            return jsonify({'api_key':api_key,'api_secret':generate_password_hash(api_secret)})
        else:
            return False

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


@app.route('/admin',methods=['GET','POST'])
def admin_panel():
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


@app.route('/lo')
def logout():
    if 'admin' in session:
        session.pop('admin',None)
    session.pop('logged_in_user',None)
    return redirect(url_for('home'))


@app.route('/blog')
def blogmain():
    error = None
    start_time = time.time()
    num_entries = 5
    #print(request.args.get('p'))
    try:
        offset = int(request.args.get('p')) * num_entries
    except:
        offset = 0
    if offset < 0:
        return redirect(url_for('blogmain'))
    blogposts = get_blogposts(num_entries,offset=offset)
    if blogposts['total']<=offset and blogposts['total']>0:
        return redirect(url_for('blogmain'))
    return render_template('blog.html',full=True,offset=offset,blogposts=blogposts,error=error, processtime=round(time.time()-start_time,5))


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
        arguments['search_terms']= [ item.encode('utf-8') for item in request.args.get('search').split(' ')[:10]]
    # try:
    entries = get_entries(num_entries,**arguments)
    # except:
    #   error = 'Malformed request for entries!'
    #   return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))
    if entries['total']<=arguments['offset'] and entries['total']>0:
        return redirect(url_for('allmain'))
    return render_template('all.html',full=True,offset=arguments['offset'],recents=entries,error=error, processtime=round(time.time()-start_time,5))


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


@app.route('/blog/<id>')
def blogindividual(id):
    error = None
    start_time = time.time()
    try:
        blogid = int(id)
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute("SELECT id,time,author,title,post,live FROM blog WHERE id="+app.sqlesc+" AND live='1'",(blogid,))
        blogdata = cur.fetchone()
        if blogdata != None:
            blogdata = list(blogdata)
            blogdata[1] = datetime.datetime.fromtimestamp(blogdata[1])
            blogposts = {'posts':(blogdata,),'total':1}
            return render_template('blog.html',full=True,offset=0,recents=get_recents(),blogposts=blogposts,error=error, processtime=round(time.time()-start_time,5))
        else:
            error = "No blog with that ID!"
    except:
        error = "No blog with that ID!"
    return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))


@app.route('/dl/<url>')
def retrieve_file(url):
    error=None
    start_time = time.time()
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute("SELECT savefileLocation,name,uniqueIDForThisGame,download_enabled,download_url,id FROM playerinfo WHERE url="+app.sqlesc,(url,))
    result = cur.fetchone()
    if result[3] == True:
        if result[4] == None:
            filename = generateSavegame.createZip(url,result[1],result[2],'static/saves',result[0])
            cur.execute('UPDATE playerinfo SET download_url='+app.sqlesc+' WHERE id='+app.sqlesc,(filename,result[5]))
            g.db.commit()
            return redirect(filename)
        else:
            return redirect(result[4])
    elif 'admin' in session:
        if result != None:
            with open(result[0],'rb') as f:
                response = make_response(f.read())
            response.headers["Content-Disposition"] = "attachment; filename="+str(result[1])+'_'+str(result[2])
            return response
        else:
            error = "URL does not exist"
    else:
        error = "You are unable to download this farm data at this time."
    return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))


@app.route('/faq')
def faq():
    error = None
    start_time=time.time()
    return render_template('faq.html',error=error,processtime=round(time.time()-start_time,5))


@app.route('/imgur')
def get_imgur_auth_code():
    start_time = time.time()
    error = None
    if logged_in():
        if len(request.args)==0:
            return redirect(imgur.getAuthUrl(get_logged_in_user(),target=url_for('account_page')))
        else:
            result = imgur.swapCodeForTokens(request.args)
            if result['success']==True:
                return redirect(result['redir'])
            else:
                error = "Problem authenticating at imgur!"
                return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))
    else:
        error = "Cannot connect to imgur if not logged in!"
        return render_template('error.html',error=error,processtime=round(time.time()-start_time,5))

if __name__ == "__main__":
    app.run()
