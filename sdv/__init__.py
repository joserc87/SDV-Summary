#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, redirect, url_for, request, flash, g, jsonify, make_response, send_from_directory, abort
from flask_recaptcha import ReCaptcha
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from werkzeug import secure_filename, check_password_hash
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.security import generate_password_hash
from google_measurement_protocol import Event, report
import time
import os
import sys
import json
import hashlib
from xml.etree.ElementTree import ParseError
import operator
import random
import sqlite3
import datetime
import uuid
import io
import sdv.imgur
import defusedxml
import psycopg2
from sdv.playerInfo import playerInfo
from sdv.farmInfo import getFarmInfo
from sdv.bigbase import dec2big

from config import config

from sdv.createdb import database_structure_dict, database_fields
from sdv.savefile import savefile
from sdv.zipuploads import zopen, zwrite

if sys.version_info >= (3, 0):
    unicode = str
else:
    str = unicode

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

recaptcha = ReCaptcha()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('SDV_APP_SETTINGS', 'development')

    app.config.from_object(config[config_name])
    recaptcha.init_app(app=app)
    bcrypt.init_app(app)
    mail.init_app(app)

    app.secret_key = app.config['SECRET_KEY']
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.wsgi_app = ProxyFix(app.wsgi_app)
    if app.config['USE_SQLITE'] == True:
        app.database = app.config['DB_SQLITE']
        app.sqlesc = '?'
        def connect_db():
            return sqlite3.connect(app.database)
    else:
        app.database = 'dbname='+app.config['DB_NAME']+' user='+app.config['DB_USER']+' password='+app.config['DB_PASSWORD']
        app.sqlesc = '%s'

    return app

app = create_app()


def connect_db():
    return psycopg2.connect(app.database)

def legacy_location(location):
    '''
    this allows for the move from flat-file app to modular app. it's really hacky.
    it should be used ONLY on READ and WRITE commands, NEVER to modify a filename before saving to db - or it'll be
    reapplied later when that filename is read, and you'll end up with LEGACY_ROOT_FOLDER being prepended twice...
    '''
    return os.path.join(app.config['LEGACY_ROOT_FOLDER'],location)
app.jinja_env.globals.update(legacy_location=legacy_location)

import sdv.imageDrone  # noqa
import sdv.emailDrone  # noqa
import sdv.generateSavegame # noqa

def get_db():
    # designed to prevent repeated db connections
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_db()
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()


def page_init():
    if not hasattr(g,'start_time'):
        g.start_time = time.time()
    if not hasattr(g,'error'):
        g.error = None


def page_args():
    return {'processtime':round(time.time()-g.start_time,5),'error':g.error}


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
    recents = get_recents()['posts']
    votes = None
    if logged_in():
        votes = {}
        for recent in recents:
            votes[recent[0]] = get_votes(recent[0])
    return jsonify(recents=recents,votes=votes)


def check_user_pw(email,password_attempt):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id,password,auth_key FROM users WHERE email='+app.sqlesc,(email,))
    result = cur.fetchall()
    assert len(result) <= 1
    if len(result) == 0:
        return {'result':False, 'error':'Username not found!'}
    else:
        hash_type = _get_hash_type(result[0][1])
        if hash_type == 'sha1':
            password_valid = check_password_hash(result[0][1],password_attempt)
            if password_valid:
                new_hash = bcrypt.generate_password_hash(password_attempt)
                cur.execute('UPDATE users SET password='+app.sqlesc+' WHERE email='+app.sqlesc,(new_hash,email))
                db.commit()
        elif hash_type == 'bcrypt':
            password_valid = bcrypt.check_password_hash(result[0][1],password_attempt)
        else:
            return {'result':False,'error':'Unable to interpret stored password hash!'}
        if password_valid == True:
            if result[0][2] == None:
                auth_key = dec2big(random.randint(0,(2**128)))
                cur.execute('UPDATE users SET auth_key='+app.sqlesc+', login_time='+app.sqlesc+' WHERE id='+app.sqlesc,(auth_key,time.time(),result[0][0]))
                db.commit()
            else:
                auth_key = result[0][2]
            session['logged_in_user']=(result[0][0],auth_key)
            return {'result':True}
        else:
            return {'result':False,'error':'Incorrect password!'}


def _get_hash_type(hashed_pw):
    split_hash = hashed_pw.split('$')
    if split_hash[0] == 'pbkdf2:sha1:1000':
        return 'sha1'
    elif split_hash[1] == '2b' and split_hash[0] == '':
        return 'bcrypt'
    else:
        raise TypeError


@app.route('/login', methods=['GET','POST'])
def login():
    page_init()
    session.permanent = True
    if logged_in():
        return redirect(url_for('home'))
    if request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
            g.error = 'Missing email or password for login!'
        else:
            pw = check_user_pw(request.form['email'],request.form['password'])
            if pw['result'] != True:
                g.error = pw['error']
            else:
                flash({'message':'<p>Logged in successfully!</p>'})
                return redirect(url_for('home'))
    return render_template("login.html",**page_args())


@app.route('/reset', methods=['GET','POST'])
def reset_password():
    page_init()
    if request.method == 'POST':
        if 'email' in request.form and request.form['email']!='':
            db = get_db()
            cur = db.cursor()
            cur.execute('SELECT id, email_confirmed FROM users WHERE email='+app.sqlesc,(request.form['email'],))
            result = cur.fetchall()
            if len(result) == 0:
                g.error = 'Username not found!'
            elif result[0][1] != True:
                g.error = 'Email address not verified; please verify your account using the verification email sent when you registered before attempting to reset password!'
            else:
                cur.execute('SELECT users.id FROM users WHERE email='+app.sqlesc+' AND NOT EXISTS (SELECT todo.id FROM todo WHERE todo.playerid=CAST(users.id AS text))',(request.form['email'],))
                user_id = cur.fetchone()
                if user_id != None:
                    cur.execute('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',('email_passwordreset',user_id[0]))
                    db.commit()
                    emailDrone.process_email()
                    flash({'message':'<p>Password reset email sent!</p>'})
                else:
                    flash({'message':'<p>Previous password reset email still waiting to be sent... (sorry)</p>'})
                return redirect(url_for('home'))
        elif 'password' in request.form and len(request.form['password'])>=	app.config['PASSWORD_MIN_LENGTH'] and 'id' in request.form and 'pw_reset_token' in request.form:
            db = get_db()
            cur = db.cursor()
            cur.execute('SELECT pw_reset_token, id FROM users WHERE id='+app.sqlesc,(request.form['id'],))
            t = cur.fetchall()
            if len(t) == 0:
                g.error = 'Cannot reset password: account does not exist'
                return render_template('error.html',**page_args())
            elif t[0][0] == None:
                flash({'message':'<p>This reset link has already been used!</p>'})
                return redirect(url_for('home'))
            else:
                if t[0][0] == request.args.get('t'):
                    new_hash = bcrypt.generate_password_hash(request.form['password'])
                    cur.execute('UPDATE users SET password='+app.sqlesc+', pw_reset_token=NULL WHERE id='+app.sqlesc,(new_hash,request.form['id']))
                    db.commit()
                    flash({'message':'<p>Password reset, please log in!</p>'})
                    return redirect(url_for('login'))
            g.error = 'Malformed verification string!'
            return render_template('error.html',**page_args())
        elif 'password' in request.form and len(request.form['password'])< app.config['PASSWORD_MIN_LENGTH']:
            g.error = 'Password insufficiently long, please try again'
        else:
            g.error = 'Please enter the email address you used to register'
    if 'i' in request.args and 't' in request.args:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT pw_reset_token, email, id FROM users WHERE id='+app.sqlesc,(request.args.get('i'),))
        t = cur.fetchall()
        if len(t) == 0:
            g.error = 'Cannot reset password: account does not exist'
            return render_template('error.html',**page_args())
        elif t[0][0] == None:
            flash({'message':'<p>This reset link has already been used!</p>'})
            return redirect(url_for('home'))
        else:
            if t[0][0] == request.args.get('t'):
                return render_template("reset.html",details=t[0],**page_args())
        g.error = 'Malformed verification string!'
        return render_template('error.html',**page_args())
    return render_template("reset.html",**page_args())


@app.route('/su',methods=['GET','POST'])
def signup():
    page_init()
    if 'logged_in_user' in session:
        g.error = 'You are already logged in!'
    elif request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form or request.form['email']=='':
            g.error = 'Missing email or password!'
        elif len(request.form['password'])<app.config['PASSWORD_MIN_LENGTH']:
            g.error = 'Password too short!'
        else:
            if recaptcha.verify():
                db = get_db()
                cur = db.cursor()
                cur.execute('SELECT id FROM users WHERE email='+app.sqlesc,(request.form['email'],))
                result = cur.fetchall()
                if len(result) == 0:
                    if len(request.form['email'].split('@')) == 2 and len(request.form['email'].split('@')[1].split('.'))>= 2:
                        cur.execute('INSERT INTO users (email,password) VALUES ('+app.sqlesc+','+app.sqlesc+') RETURNING id',(request.form['email'],bcrypt.generate_password_hash(request.form['password'])))
                        user_id = cur.fetchall()[0][0]
                        cur.execute('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',('email_confirmation',user_id))
                        db.commit()
                        emailDrone.process_email()
                        flash({'message':'<p>You have successfully registered. A verification email has been sent to you. Now, please sign in!</p>'})
                        return redirect(url_for('login'))
                    else:
                        g.error = 'Invalid email address!'
                else:
                    g.error = 'This email address has already registered'
            else:
                g.error = 'Captcha failed! If you are human, please try again!'
    return render_template("signup.html",**page_args())


@app.route('/acc',methods=['GET','POST'])
def account_page():
    page_init()
    if not logged_in():
        g.error = 'You must be signed in to view your profile!'
        return render_template("login.html",**page_args())
    else:
        user = get_logged_in_user()
        claimables = find_claimables()
        db = get_db()
        c = db.cursor()
        if request.method == 'POST':
            if 'privacy_default' in request.form and request.form.get('privacy_default') in ['True','False']:
                # print c.mogrify('UPDATE users SET privacy_default='+app.sqlesc+' WHERE id='+app.sqlesc,(True if request.form.get('privacy_default') == 'True' else False,user)).decode('utf-8')
                c.execute('UPDATE users SET privacy_default='+app.sqlesc+' WHERE id='+app.sqlesc,(True if request.form.get('privacy_default') == 'True' else False,user))
                db.commit()
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
        c.execute('SELECT email,imgur_json,privacy_default FROM users WHERE id='+app.sqlesc,(user,))
        e = c.fetchone()
        acc_info = {'email':e[0],'imgur':json.loads(e[1]) if e[1] != None else None, 'privacy_default':e[2]}
        has_liked = True if True in has_votes(user).values() else False
        return render_template('account.html',claimed=claimed_ids,claimable=claimable_ids, has_liked=has_liked, acc_info=acc_info,**page_args())


def logged_in():
    # designed to prevent repeated db requests
    if not hasattr(g,'logged_in_user'):
        if 'logged_in_user' in session:
            db = get_db()
            cur = db.cursor()
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


def add_to_series(rowid,uniqueIDForThisGame,name,farmName):
    current_auto_key = json.dumps([uniqueIDForThisGame,name,farmName])
    db = get_db()
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
        g.error = "I don't think that's very funny"
        return {'type':'render','target':'index.html','parameters':{"error":g.error}}
    except IOError:
        g.error = "Savegame failed sanity check (if you think this is in error please let us know)"
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),'failed sanity check '+str(secure_filename(inputfile.filename))))
        db.commit()
        return {'type': 'render', 'target': 'index.html', 'parameters': {"error": g.error}}
    except AttributeError as e:
        g.error = "Not valid save file - did you select file 'SaveGameInfo' instead of 'playername_number'?"
        print(e)
        return {'type': 'render', 'target': 'index.html', 'parameters': {"error": g.error}}
    except ParseError as e:
        g.error = "Not well-formed xml"
        return {'type':'render','target':'index.html','parameters':{"error":g.error}}
    dupe = is_duplicate(md5_info,player_info)
    if dupe != False:
        session[dupe[0]] = md5_info
        session[dupe[0]+'del_token'] = dupe[1]
        return {'type':'redirect','target':'display_data','parameters':{"url":dupe[0]}}
        return redirect(url_for('display_data',url=dupe[0]))
    else:
        farm_info = getFarmInfo(save)
        outcome, del_token, rowid, g.error = insert_info(player_info,farm_info,md5_info)
        if outcome != False:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], outcome)
            # with open(filename,'wb') as f:
            # 	f.write(memfile.getvalue())
            # REPLACED WITH ZIPUPLOADS
            zwrite(memfile.getvalue(),legacy_location(filename))
            series_id = add_to_series(rowid,player_info['uniqueIDForThisGame'],player_info['name'],player_info['farmName'])
            owner_id = get_logged_in_user()
            db = get_db()
            cur = db.cursor()
            cur.execute('UPDATE playerinfo SET savefileLocation='+app.sqlesc+', series_id='+app.sqlesc+', owner_id='+app.sqlesc+' WHERE url='+app.sqlesc+';',(filename,series_id,owner_id,outcome))
            db.commit()
        else:
            if g.error == None:
                g.error = "Error occurred inserting information into the database!"
            return {'type':'render','target':'index.html','parameters':{"error":g.error}}
        imageDrone.process_queue()
        memfile.close()
    if outcome != False:
        session.permanent = True
        session[outcome] = md5_info
        session[outcome+'del_token'] = del_token
        return {'type':'redirect','target':'display_data','parameters':{"url":outcome}}


@app.route('/',methods=['GET','POST'])
def home():
    page_init()
    if request.method == 'POST':
        inputfile = request.files['file']
        if inputfile:
            result = file_uploaded(inputfile)
            if result['type'] == 'redirect':
                return redirect(url_for(result['target'],**result['parameters']))
            elif result['type'] == 'render':
                params = {'blogposts':get_blogposts(5),'recents':get_recents()}
                if 'parameters' in result:
                    for key in result['parameters'].keys():
                        params[key] = result['parameters'][key]
                return render_template(result['target'], **params)
    recents = get_recents()
    vote = json.dumps({entry[0]:get_votes(entry[0]) for entry in recents['posts']})
    return render_template("index.html", recents=recents, vote=vote, blogposts=get_blogposts(5), **page_args())

@app.route('/api/v1/plan',methods=['PUT'])
def api_v1_plan():
    if request.method == 'PUT':
        # check rate limiter; if all good, continue, else return status:'overlimit'
        # check_rate_limiter()
        # check input json for validity
        verify_json(request.form)
        # insert it to a database, checking for duplicates(?)
        add_plan(request.form['plan_as_text'],request.form['source_url'])
        # queue a rendering job
        # insert_into_tasklist()
        # optional: run imageDrone with a json parameter to tell it only to render json jobs?
        # imageDrone('json')
        # return status:'success' or status:'failedrender'; url, id
        return jsonify({'status':'success'})

def verify_json(form):
    assert 'plan_as_text' in form
    assert 'source_url' in form


def add_plan(source_json, planner_url):
    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO plans (added_time,source_json,planner_url,views) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+') RETURNING id, added_time;',(time.time(),source_json,planner_url,0))
    row = cur.fetchone()
    url = dec2big(int(row[0])+int(row[1]))
    cur.execute('UPDATE plans SET url='+app.sqlesc+' WHERE id='+app.sqlesc+'',(url,row[0]))
    db.commit()

def render_from_json():
    # we need a new class of image render for imageDrone to handle and a new class of profile to display it!
    print('render_from_json does nothing yet')
    return({'status':'renderfromjsondoesnothingyet','id':'idnumber','url':'url_of_resulting_image'})

'''
# DEPRECIATED 'API' CODE
# left in as reminder of how it worked; remove once new api complete

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
        db = get_db()
        cur = db.cursor()
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
                db.commit()
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
        db = get_db()
        cur = db.cursor()
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
                db.commit()
            else:
                api_key = result[0][2]
                api_secret = result[0][3]
            return jsonify({'api_key':api_key,'api_secret':generate_password_hash(api_secret)})
        else:
            return False
'''

def get_recents(n=6,**kwargs):
    recents = get_entries(n,**kwargs)
    return recents


def is_duplicate(md5_info,player_info):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, md5, name, uniqueIDForThisGame, url, del_token FROM playerinfo WHERE md5='+app.sqlesc,(md5_info,))
    matches = cur.fetchall()
    if len(matches) > 0:
        for match in matches:
            if str(player_info['name'])==str(match[2]) and str(player_info['uniqueIDForThisGame'])==str(match[3]):
                return (match[4],match[5])
        return False
    else:
        return False


def get_privacy():
    if not hasattr(g,'logged_in_privacy_default'):
        if logged_in():
            db = get_db()
            cur = db.cursor()
            cur.execute('SELECT privacy_default FROM users WHERE id='+app.sqlesc,(get_logged_in_user(),))
            g.logged_in_privacy_default = cur.fetchone()[0]
        else:
            g.logged_in_privacy_default = None
    return g.logged_in_privacy_default

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
    if get_privacy() != None:
        columns.append('private')
        values.append(get_privacy())
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
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('INSERT INTO playerinfo ('+colstring+') VALUES ('+questionmarks+') RETURNING id,added_time',tuple(values))
        row = cur.fetchone()
        url = dec2big(int(row[0])+int(row[1]))
        rowid = row[0]
        cur.execute('UPDATE playerinfo SET url='+app.sqlesc+' WHERE id='+app.sqlesc+'',(url,rowid))
        cur.execute('INSERT INTO todo (task, playerid) VALUES ('+app.sqlesc+','+app.sqlesc+')',('process_image',rowid))
        db.commit()
        return url, del_token, rowid, None
    except (sqlite3.OperationalError, psycopg2.ProgrammingError) as e:
        db.rollback()
        cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),str(e)+' '+json.dumps([columns,values])))
        db.commit()
        return False, del_token, False, "Save file incompatible with current database: error is "+str(e)


@app.route('/<url>')
def display_data(url):
    page_init()
    deletable = None
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE url='+app.sqlesc+'',(url,))
    data = cur.fetchall()
    if len(data) != 1:
        g.error = 'There is nothing here... is this URL correct?'
        if str(url) != 'favicon.ico':
            cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),str(len(data))+' cur.fetchall() for url:'+str(url)))
            db.commit()
        return render_template("error.html", **page_args())
    else:
        cur.execute('UPDATE playerinfo SET views=views+1 WHERE url='+app.sqlesc+'',(url,))
        db.commit()
        datadict = {}
        for k, key in enumerate(sorted(database_structure_dict.keys())):
            if key != 'farm_info':
                datadict[key] = data[0][k]
        claimable = False
        deletable = False
        if datadict['owner_id'] == None:
            if url in session and url+'del_token' in session and session[url] == datadict['md5'] and session[url+'del_token'] == datadict['del_token']:
                if logged_in():
                    claimable = True
                else:
                    deletable = True
        elif logged_in() and str(datadict['owner_id']) == str(get_logged_in_user()):
            deletable = True

        other_saves, gallery_set = get_others(datadict['url'],datadict['date'],datadict['map_url'])
        for item in ['money','totalMoneyEarned','statsStepsTaken','millisecondsPlayed']:
            if item == 'millisecondsPlayed':
                datadict[item] = "{:,}".format(round(float((int(datadict[item])/1000)/3600.0),1))
            else:
                datadict[item] = "{:,}".format(datadict[item])

        datadict['animals'] = None if datadict['animals']=='{}' else json.loads(datadict['animals'])
        datadict['portrait_info'] = json.loads(datadict['portrait_info'])
        friendships = sorted([[friendship[11:],datadict[friendship]] for friendship in sorted(database_structure_dict.keys()) if friendship.startswith('friendships') and datadict[friendship]!=None],key=lambda x: x[1])[::-1]
        kills = sorted([[kill[27:].replace('_',' '),datadict[kill]] for kill in sorted(database_structure_dict.keys()) if kill.startswith('statsSpecificMonstersKilled') and datadict[kill]!=None],key=lambda x: x[1])[::-1]
        if datadict['imgur_json']!=None:
            datadict['imgur_json'] = json.loads(datadict['imgur_json'])
        # passworded = True if datadict['del_password'] != None else False
        # passworded=passworded, removed from next line
        claimables = find_claimables()
        vote = json.dumps({url:get_votes(url)})
        if logged_in() == False and len(claimables) > 1 and request.cookies.get('no_signup')!='true':
            flash({'message':"<p>It looks like you have uploaded multiple files, but are not logged in: if you <a href='{}'>sign up</a> or <a href='{}'>sign in</a> you can link these uploads, enable savegame sharing, and one-click-post farm renders to imgur!</p>".format(url_for('signup'),url_for('login')),'cookie_controlled':'no_signup'})
        return render_template("profile.html", deletable=deletable, claimable=claimable, claimables=claimables, vote=vote,data=datadict, kills=kills, friendships=friendships, others=other_saves, gallery_set=gallery_set, **page_args())


def get_others(url,date,map_url):
    return_data = {}
    gallery_set = {'order':[],'lookup':{}}
    try:
        arguments = {'series':url,'sort_by':'chronological'}
        results = get_entries(1000,**arguments)['posts'][::-1]
        current_index = list(zip(*results))[0].index(url)
        for j,i in enumerate(range(current_index-1, current_index+2)):
            if i>=0 and i<len(results):
                return_data[['previous','current','next'][j]] = (results[i][0],results[i][3])
        for row in results:
            gallery_set['order'].append(row[7])
            gallery_set['lookup'][row[7]]=[row[0],row[3]]
    except (ValueError, IndexError):
        # this would occur in the case of a private page being viewed by a non-logged-in user; get_entries() will return nothing
        return_data['current'] = (url,date,map_url)
        gallery_set['order'].append(map_url)
        gallery_set['lookup'][map_url]=[url,date]
    gallery_set = {'json':json.dumps(gallery_set),'dict':gallery_set}
    return return_data, gallery_set


def find_claimables():
    if not hasattr(g,'claimables'):
        sessionids = list(session.keys())
        removals = ['admin','logged_in_user']
        for key in removals:
            try:
                sessionids.remove(key)
            except ValueError:
                pass
        urls = tuple([key for key in sessionids if not key.endswith('del_token')])
        if len(urls) > 0:
            db = get_db()
            cur = db.cursor()
            cur.execute('SELECT id, md5, del_token, url FROM playerinfo WHERE owner_id IS NULL AND url IN '+app.sqlesc,(urls,))
            result = cur.fetchall()
            checked_results = []
            for row in result:
                if row[1] == session[row[3]] and row[2] == session[row[3]+'del_token']:
                    checked_results.append((row[0],row[3]))
            g.claimables = checked_results
        else:
            g.claimables = []
    return g.claimables


@app.route('/<url>/<instruction>',methods=['GET','POST'])
def operate_on_url(url,instruction):
    page_init()
    if request.method == 'POST':
        if (url in session and url+'del_token' in session) or logged_in():
            db = get_db()
            cur = db.cursor()
            # first: if logged in, get the URL, MD5 and deletion token for all farms owned by user; set session cookies indicating this ownership for all
            _op_set_ownership_cookies()

            if instruction == 'del':
                return _op_del(url)
            elif instruction == 'delall':
                return _op_delall(url)

            elif instruction == 'claim':
                return _op_claim(url)
            elif instruction == 'claimall':
                return _op_claimall(url)

            elif instruction == 'enable-dl':
                return _op_toggle_boolean_param(url,'download_enabled',True)
            elif instruction == 'disable-dl':
                return _op_toggle_boolean_param(url,'download_enabled',False)

            elif instruction == 'imgur':
                return _op_imgur_post(url)

            elif instruction == 'list':
                return _op_toggle_boolean_param(url,'private',False)
            elif instruction == 'unlist':
                return _op_toggle_boolean_param(url,'private',True)
        g.error = "Unknown or insufficient credentials"
        return render_template("error.html", **page_args())
    else:
        return redirect(url_for('display_data',url=url))


def _op_set_ownership_cookies():
    db = get_db()
    cur = db.cursor()
    if logged_in():
        cur.execute('SELECT url,md5,del_token FROM playerinfo WHERE owner_id='+app.sqlesc,(get_logged_in_user(),))
        result = cur.fetchall()
        for row in result:
            if not row[0] in session:
                session[row[0]]=row[1]
            if not row[0]+'del_token' in session:
                session[row[0]+'del_token']=row[2]


def _op_del(url):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT owner_id FROM playerinfo WHERE url='+app.sqlesc,(url,))
    data = cur.fetchone()
    if str(data[0]) == str(get_logged_in_user()):
        outcome = delete_playerinfo_entry(url,session[url],session[url+'del_token'])
        if outcome == True:
            return redirect(url_for('home'))
        else:
            g.error = outcome
    else:
        g.error = 'You do not own this farm'
    return render_template("error.html", **page_args())


def _op_delall(url):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT url,owner_id FROM playerinfo WHERE series_id=(SELECT series_id FROM playerinfo WHERE url='+app.sqlesc+')',(url,))
    data = cur.fetchall()
    for row in data:
        if str(row[1]) != str(get_logged_in_user()):
            g.error = 'You do not own at least one of the farms'
            return render_template("error.html", **page_args())
    # verified logged_in_user owns all farms
    for row in data:
        outcome = delete_playerinfo_entry(row[0],session[row[0]],session[row[0]+'del_token'])
        if outcome != True:
            g.error = outcome
            return render_template("error.html", **page_args())
    return redirect(url_for('home'))


def _op_claim(url):
    db = get_db()
    cur = db.cursor()
    if url in [url for rowid, url in find_claimables()]:
        outcome = claim_playerinfo_entry(url,session[url],session[url+'del_token'])
        if outcome == True:
            return redirect(url_for('display_data',url=url))
        else:
            g.error = outcome
    else:
        g.error = 'You do not have sufficient credentials to claim this page'
    return render_template("error.html", **page_args())


def _op_claimall(url):
    db = get_db()
    cur = db.cursor()
    for rowid, claim_url in find_claimables():
        outcome = claim_playerinfo_entry(claim_url,session[claim_url],session[claim_url+'del_token'])
        if outcome != True:
            g.error = 'You do not have sufficient credentials to claim one of these pages'
    return redirect(url_for('display_data',url=url))


def _op_toggle_boolean_param(url,param,state):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT owner_id,id FROM playerinfo WHERE url='+app.sqlesc,(url,))
    data = cur.fetchone()
    if str(data[0]) == str(get_logged_in_user()):
        cur = db.cursor()
        cur.execute('UPDATE playerinfo SET '+param+'='+app.sqlesc+' WHERE id='+app.sqlesc,(state,data[1],))
        db.commit()
        return redirect(url_for('display_data',url=url))
    else:
        g.error = 'You do not have sufficient credentials to perform this action'
        return render_template("error.html", **page_args())


def _op_imgur_post(url):
    db = get_db()
    cur = db.cursor()
    if logged_in():
        check_access = imgur.checkApiAccess(get_logged_in_user())
        if check_access == True:
            result = imgur.uploadToImgur(get_logged_in_user(),url)
            if 'success' in result:
                return redirect(result['link'])
            elif 'error' in result:
                if result['error'] == 'too_soon':
                    g.error = 'You have uploaded this page to imgur in the last 2 hours: please wait to upload again'
                elif result['error'] == 'upload_issue':
                    g.error = 'There was an issue with uploading the file to imgur. Please try again later!'
            else:
                g.error = 'There was an unknown error!'
            return render_template("error.html", **page_args())
        elif check_access == False:
            return redirect(imgur.getAuthUrl(get_logged_in_user(),target=request.path))
        elif check_access == None:
            g.error = 'Either you or upload.farm are out of imgur credits for the day! Sorry :( Try again tomorrow'
            return render_template("error.html", **page_args())
    else:
        g.error = "You must be logged in to post your farm to imgur!"
        return render_template("signup.html", **page_args())


def delete_playerinfo_entry(url,md5,del_token):
    # takes url, md5, and del_token (from session); if verified, deletes
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id,md5,del_token,url,savefileLocation,avatar_url,portrait_url,map_url,farm_url,download_url,thumb_url,base_path,owner_id,series_id FROM playerinfo WHERE url='+app.sqlesc,(url,))
    result = cur.fetchone()
    if result[1] == md5 and result[2] == del_token and str(result[12]) == str(get_logged_in_user()):
        if remove_series_link(result[0],result[13]) == False:
            pass #return 'Problem removing series link!'
        cur.execute('DELETE FROM playerinfo WHERE id=('+app.sqlesc+')',(result[0],))
        for filename in result[4:11]:
            if filename != None and os.path.split(os.path.split(filename)[0])[1] == result[3]:
                # second condition ensures you're in a folder named after the URL which prevents accidentally deleting placeholders
                try:
                    os.remove(filename)
                except:
                    pass
        try:
            os.rmdir(result[11])
        except:
            pass
        db.commit()
        session.pop(url, None)
        session.pop(url+'del_token', None)
        return True
    else:
        return 'You do not have the correct session information to perform this action!'


def remove_series_link(rowid, series_id):
    # removes a link to playerinfo id (rowid) from id in series (series_id)
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT members_json FROM series WHERE id='+app.sqlesc,(series_id,))
    a = cur.fetchone()
    result = json.loads(a[0]) if a != None else None
    try:
        result.remove(int(rowid))
    except (ValueError,AttributeError):
        return False
    if len(result) == 0:
        cur.execute('DELETE FROM series WHERE id='+app.sqlesc,(series_id,))
        cur.execute('UPDATE playerinfo SET series_id=NULL WHERE id='+app.sqlesc,(rowid,))
    else:
        cur.execute('UPDATE series SET members_json='+app.sqlesc+' WHERE id='+app.sqlesc,(json.dumps(result),series_id))
        cur.execute('UPDATE playerinfo SET series_id=NULL WHERE id='+app.sqlesc,(rowid,))
    db.commit()
    return True


def claim_playerinfo_entry(url,md5,del_token):
    # verify ability to be owner, then remove_series_link (checking ownership!), then add_to_series
    if logged_in():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT id,series_id,md5,del_token,owner_id,uniqueIDForThisGame,name,farmName FROM playerinfo WHERE url='+app.sqlesc,(url,))
        result = cur.fetchone()
        if result[2] == md5 and result[3] == del_token and result[4] == None:
            remove_series_link(result[0], result[1])
            series_id = add_to_series(result[0],result[5],result[6],result[7])
            cur.execute('UPDATE playerinfo SET series_id='+app.sqlesc+', owner_id='+app.sqlesc+' WHERE id='+app.sqlesc,(series_id,get_logged_in_user(),result[0]))
            db.commit()
            return True
        else:
            return 'Problem authenticating!'
    else:
        return 'You are not logged in!'


@app.route('/admin',methods=['GET','POST'])
def admin_panel():
    page_init()
    if 'admin' in session:
        #trusted
        returned_blog_data = None
        db = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            if request.form['blog'] == 'Post':
                live = False
                if 'live' in request.form:
                    if request.form['live']=='on':
                        live = True
                if request.form['content'] == '' or request.form['blogtitle'] == '':
                    g.error = 'Failed to post blog entry, title or body was empty!'
                    returned_blog_data = {'blogtitle':request.form['blogtitle'],
                                          'content':request.form['content'],
                                          'checked': live}
                else:
                    cur.execute('INSERT INTO blog (time, author, title, post, live) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(int(time.time()),session['admin'],request.form['blogtitle'],request.form['content'],live))
                    db.commit()
                    if live == True:
                        flash('Posted blog entry "'+str(request.form['blogtitle']+'"'))
                    else:
                        flash('Saved unposted blog entry "'+str(request.form['blogtitle']+'"'))
            elif request.form['blog'] == 'update':
                state = request.form['live'] == 'true'
                cur.execute('UPDATE blog SET live='+app.sqlesc+' WHERE id='+app.sqlesc,(state,request.form['id']))
                db.commit()
                return 'Success'
            elif request.form['blog'] == 'delete':
                cur.execute('DELETE FROM blog WHERE id='+app.sqlesc,(request.form['id'],))
                db.commit()
                return 'Success'
        cur.execute('SELECT url,name,farmName,date FROM playerinfo')
        entries = cur.fetchall()
        return render_template('adminpanel.html',returned_blog_data=returned_blog_data,blogposts=get_blogposts(include_hidden=True),entries=entries,**page_args())
    else:
        if request.method == 'POST':
            if 'blog' in request.form:
                return 'Failure'
            else:
                try:
                    db = get_db()
                    cur = db.cursor()
                    cur.execute('SELECT password FROM admin WHERE username='+app.sqlesc+' ORDER BY id',(request.form['username'],))
                    r = cur.fetchone()
                    if r != None:
                        if check_password_hash(r[0],request.form['password']) == True:
                            session['admin']=request.form['username']
                            return redirect(url_for('admin_panel'))
                    cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'], time.time(),'failed login: '+request.form['username']))
                    db.commit()
                    g.error = 'Incorrect username or password'
                except:
                    pass
        return render_template('admin.html',**page_args())


def get_blogposts(n=False,**kwargs):
    db = get_db()
    cur = db.cursor()
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
    page_init()
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
    return render_template('blog.html',full=True,offset=offset,blogposts=blogposts,**page_args())


@app.route('/all')
def allmain():
    page_init()
    num_entries = 18
    #print(request.args.get('p'))
    arguments = {'include_failed':True}
    try:
        arguments['offset'] = int(request.args.get('p')) * num_entries
    except TypeError:
        arguments['offset'] = 0
    except:
        g.error = "No browse with that ID!"
        return render_template('error.html',**page_args())
    if arguments['offset'] < 0:
        return redirect(url_for('allmain'))
    #adapt get_recents() to take a kwarg for sort type; sort type can be GET value: /all&sort=popular
    arguments['sort_by'] = request.args.get('sort') if request.args.get('sort') != None else 'recent'
    if 'search' in request.args:
        arguments['search_terms']= [ item.encode('utf-8') for item in request.args.get('search').split(' ')[:10]]
    if 'series' in request.args:
        arguments['series'] = request.args.get('series')
    if 'liked' in request.args:
        arguments['liked'] = True if request.args.get('liked')=='True' else False
    if 'dl' in request.args:
        arguments['dl'] = True if request.args.get('dl')=='True' else False
    if 'full_thumbnail' in request.args:
        arguments['full_thumbnail'] = True if request.args.get('full_thumbnail')=='True' else False
    try:
        entries = get_entries(num_entries,**arguments)
    except:
        g.error = 'Malformed request for entries!'
        return render_template('error.html',**page_args())
    if entries['total']<=arguments['offset'] and entries['total']>0:
        return redirect(url_for('allmain'))
    vote = json.dumps({entry[0]:get_votes(entry[0]) for entry in entries['posts']})
    return render_template('all.html',full=True,offset=arguments['offset'],recents=entries,vote=vote,**page_args())


def get_entries(n=6,**kwargs):
    '''
    Returns n entries; has kwargs:
        include_failed	bool	if True includes uploads which failed image generation
        search_terms	text	search string
        series 			text	takes 'url' as key; finds all matching in series
        liked 			bool	if True only show results user has upvoted
        offset 			int 	to allow for pagination
        dl 				bool	if True only show results with downloads enabled
        full_thumbnail	bool	if True, return *full* thumbnails, not maps
        sort_by			text	'rating', 'views', 'recent', 'chronological'; 'rating' defined according to snippet from http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
        include_private bool	if True, return will check for admin status and include private farms (NOT FULLY IMPLEMENTED YET!)
    '''
    order_types = {'rating':'ORDER BY ((positive_votes + 1.9208) / (positive_votes + negative_votes) - 1.96 * SQRT((positive_votes*negative_votes)/(positive_votes+negative_votes)+0.9604) / (positive_votes+negative_votes)) / ( 1 + 3.8416 / (positive_votes + negative_votes)) ',
                   'views':'ORDER BY views ',
                   'recent':'ORDER BY id ',
                   'chronological':'ORDER BY millisecondsPlayed '}
    search_fields = ('name','farmName','date')
    db = get_db()
    cur = db.cursor()
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
                search+=cur.mogrify(field +' ILIKE '+app.sqlesc+' ',('%%'+item.decode('utf-8')+'%%',)).decode('utf-8')
                if f == len(search_fields)-1:
                    search+=')'
            if i == len(kwargs['search_terms'])-1:
                search+=')'
        where_contents.append(search)
    if 'series' in kwargs and kwargs['series']!=None:
        where_contents.append(cur.mogrify('series_id=(SELECT series_id FROM playerinfo WHERE url='+app.sqlesc+')',(kwargs['series'],)).decode('utf-8'))
    if 'liked' in kwargs and kwargs['liked']==True and logged_in():
        likes = [url for url, value in has_votes(get_logged_in_user()).items() if value==True ]
        if len(likes)>0:
            where_contents.append(cur.mogrify('url=ANY('+app.sqlesc+')',(likes,)).decode('utf-8'))
        else:
            where_contents.append('url=ANY(ARRAY[])')
    if 'dl' in kwargs and kwargs['dl']==True:
        where_contents.append('download_enabled=TRUE')
    if 'include_private' in kwargs and kwargs['include_private'] == True:
        pass
    # do some checking to ensure the person getting the private data is an admin
    else:
        where_contents.append(cur.mogrify('(private IS NOT TRUE OR (private IS TRUE AND owner_id='+app.sqlesc+'))',(get_logged_in_user(),)).decode('utf-8'))
    where = ''
    for c,contents in enumerate(where_contents):
        if c == 0:
            where+='WHERE '+contents+' '
        if c != 0:
            where+='AND '+contents+' '
    order = 'ORDER BY id ' if 'sort_by' not in kwargs else order_types[kwargs['sort_by']]
    thumbtype = 'thumb_url' if 'full_thumbnail' in kwargs and kwargs['full_thumbnail']==True else 'farm_url'
    query = 'SELECT url, name, farmName, date, avatar_url, '+thumbtype+', download_enabled, map_url, private FROM playerinfo '+where+order+'DESC LIMIT '+app.sqlesc
    # print('query:',query)
    offset = 0
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
    return entries


@app.route('/blog/<id>')
def blogindividual(id):
    page_init()
    try:
        blogid = int(id)
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id,time,author,title,post,live FROM blog WHERE id="+app.sqlesc+" AND live='1'",(blogid,))
        blogdata = cur.fetchone()
        if blogdata != None:
            blogdata = list(blogdata)
            blogdata[1] = datetime.datetime.fromtimestamp(blogdata[1])
            blogposts = {'posts':(blogdata,),'total':1}
            return render_template('blog.html',full=True,offset=0,recents=get_recents(),blogposts=blogposts,**page_args())
        else:
            g.error = "No blog with that ID!"
    except:
        g.error = "No blog with that ID!"
    return render_template('error.html',**page_args())


@app.route('/dl/<url>')
def retrieve_file(url):
    page_init()
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT savefileLocation,name,uniqueIDForThisGame,download_enabled,download_url,id FROM playerinfo WHERE url="+app.sqlesc,(url,))
    result = cur.fetchone()
    if result[3] == True:
        if result[4] == None:
            filename = generateSavegame.createZip(url,result[1],result[2],'static/saves',result[0])
            cur.execute('UPDATE playerinfo SET download_url='+app.sqlesc+' WHERE id='+app.sqlesc,(filename,result[5]))
            db.commit()
            return redirect(filename)
        else:
            return redirect(result[4])
    elif 'admin' in session:
        if result != None:
            with open(legacy_location(result[0]),'rb') as f:
                response = make_response(f.read())
            response.headers["Content-Disposition"] = "attachment; filename="+str(result[1])+'_'+str(result[2])
            return response
        else:
            g.error = "URL does not exist"
    else:
        g.error = "You are unable to download this farm data at this time."
    return render_template('error.html',**page_args())


@app.route('/faq')
def faq():
    page_init()
    return render_template('faq.html',**page_args())


@app.route('/imgur')
def get_imgur_auth_code():
    page_init()
    if logged_in():
        if len(request.args)==0:
            return redirect(imgur.getAuthUrl(get_logged_in_user(),target=url_for('account_page')))
        else:
            result = imgur.swapCodeForTokens(request.args)
            if result['success']==True:
                return redirect(result['redir'])
            else:
                g.error = "Problem authenticating at imgur!"
                return render_template('error.html',**page_args())
    else:
        g.error = "Cannot connect to imgur if not logged in!"
        return render_template('error.html',**page_args())


@app.route('/verify_email')
def verify_email():
    page_init()
    if 'i' in request.args and 't' in request.args:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT email_conf_token, email_confirmed FROM users WHERE id='+app.sqlesc,(request.args.get('i'),))
        t = cur.fetchall()
        if len(t) == 0:
            g.error = 'Account does not exist!'
            return render_template('error.html',**page_args())
        elif t[0][1] == True:
            flash({'message':'<p>Already confirmed email address!</p>'})
            return redirect(url_for('home'))
        else:
            if t[0][0] == request.args.get('t'):
                cur.execute('UPDATE users SET email_confirmed='+app.sqlesc+' WHERE id='+app.sqlesc,(True,request.args.get('i')))
                db.commit()
                flash({'message':"<p>Account email address confirmed!</p>"})
                return redirect(url_for('home'))
    g.error = 'Malformed verification string!'
    return render_template('error.html',**page_args())


@app.route('/_vote',methods=['POST'])
def submit_vote():
    if logged_in():
        if request.method == 'POST':
            if 'vote' in request.form:
                return json.dumps(handle_vote(get_logged_in_user(),request.form))
    else:
        return 'not logged in'


def handle_vote(logged_in_user,vote_info):
    # 1: check whether user has voted previously
    votes = has_votes(logged_in_user)
    vote = json.loads(request.form['vote']) if request.form['vote'] != '' else None
    # 2: if voted previously, modify user vote info to new vote, else add vote info to user vote
    previous = votes[request.form['url']] if request.form['url'] in votes else None
    if vote == previous:
        return True
    else:
        # subtract previous vote
        db = get_db()
        cur = db.cursor()
        if previous != None:
            prev_col = 'positive_votes' if previous == True else 'negative_votes'
            cur.execute('UPDATE playerinfo SET '+prev_col+'='+prev_col+'-1 WHERE url='+app.sqlesc,(request.form['url'],))
            votes[request.form['url']] = None
        # 3: add vote to correct column in playerinfo
        if vote != None:
            vote_col = 'positive_votes' if vote == True else 'negative_votes'
            cur.execute('UPDATE playerinfo SET '+vote_col+'='+vote_col+'+1 WHERE url='+app.sqlesc,(request.form['url'],))
            votes[request.form['url']] = vote
        votes = json.dumps(votes)
        cur.execute('UPDATE users SET votes='+app.sqlesc+' WHERE id='+app.sqlesc,(votes,logged_in_user))
        db.commit()
        return True
    # 4: commit, return


def has_votes(logged_in_user):
    if not hasattr(g,'logged_in_users_votes'):
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT votes FROM users WHERE id='+app.sqlesc,(logged_in_user,))
        votes = cur.fetchone()[0]
        g.logged_in_users_votes = json.loads(votes) if votes != None else {}
    return g.logged_in_users_votes


def get_votes(url):
    if logged_in():
        result = has_votes(get_logged_in_user())
        return result[url] if url in result else None
    else:
        return None

if __name__ == "__main__":
    app.run()