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
import json
import operator
import random
import sqlite3
import psycopg2
import datetime
from flask_recaptcha import ReCaptcha
import uuid
from google_measurement_protocol import Event, report

import uploadfarm.savehandling.generateSavegame
from uploadfarm.tools.bigbase import dec2big
from uploadfarm.imagegeneration.imageDrone import process_queue
from uploadfarm.tools.createdb import database_structure_dict, database_fields
import uploadfarm.imgur
from uploadfarm import views

from uploadfarm.blueprints import profile, blog, admin
from uploadfarm.blueprints.blog import get_blogposts
app.register_blueprint(profile, static_folder='static')
app.register_blueprint(blog, url_prefix="/blog")
app.register_blueprint(admin, url_prefix="/admin")

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


def get_logged_in_user():
    if logged_in():
        return session['logged_in_user'][0]
    else:
        return None


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
