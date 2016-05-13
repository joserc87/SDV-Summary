from flask import Blueprint, g, session, render_template, request, flash, url_for, redirect
import time
from flask import current_app as app
from uploadfarm import connect_db
from uploadfarm.createdb import database_structure_dict, database_fields
import json
import os

profile = Blueprint('profile', __name__,
                    template_folder='templates')

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


def get_logged_in_user():
    if logged_in():
        return session['logged_in_user'][0]
    else:
        return None


@profile.route('/<url>')
def display_data(url):
    error = None
    deletable = None
    start_time = time.time()
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('SELECT '+database_fields+' FROM playerinfo WHERE url='+app.sqlesc+'',(url,))
    data = cur.fetchall()
    if len(data) != 1:
        error = 'There is nothing here... is this URL correct?'
        cur.execute('INSERT INTO errors (ip, time, notes) VALUES ('+app.sqlesc+','+app.sqlesc+','+app.sqlesc+')',(request.environ['REMOTE_ADDR'],time.time(),str(len(data))+' cur.fetchall() for url:'+str(url)))
        g.db.commit()
        return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
    else:
        cur.execute('UPDATE playerinfo SET views=views+1 WHERE url='+app.sqlesc+'',(url,))
        g.db.commit()
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

        for item in ['money','totalMoneyEarned','statsStepsTaken','millisecondsPlayed']:
            if item == 'millisecondsPlayed':
                datadict[item] = "{:,}".format(round(float((int(datadict[item])/1000)/3600.0),1))
            else:
                datadict[item] = "{:,}".format(datadict[item])
        
        datadict['animals'] = None if datadict['animals']=='{}' else json.loads(datadict['animals'])
        datadict['portrait_info'] = json.loads(datadict['portrait_info'])
        friendships = sorted([[friendship[11:],datadict[friendship]] for friendship in sorted(database_structure_dict.keys()) if friendship.startswith('friendships') and datadict[friendship]!=None],key=lambda x: x[1])[::-1]
        kills = sorted([[kill[27:].replace('_',' '),datadict[kill]] for kill in sorted(database_structure_dict.keys()) if kill.startswith('statsSpecificMonstersKilled') and datadict[kill]!=None],key=lambda x: x[1])[::-1]
        cur.execute('SELECT url, date FROM playerinfo WHERE series_id='+app.sqlesc,(datadict['series_id'],))
        other_saves = cur.fetchall()
        if datadict['imgur_json']!=None:
            datadict['imgur_json'] = json.loads(datadict['imgur_json'])
        # passworded = True if datadict['del_password'] != None else False
        # passworded=passworded, removed from next line
        claimables = find_claimables()
        vote = get_votes(url)
        if logged_in() == False and len(claimables) > 1 and request.cookies.get('no_signup')!='true':
            flash({'message':"<p>It looks like you have uploaded multiple files, but are not logged in: if you <a href='{}'>sign up</a> or <a href='{}'>sign in</a> you can link these uploads, enable savegame sharing, and one-click-post farm renders to imgur!</p>".format(url_for('signup'),url_for('login')),'cookie_controlled':'no_signup'})
        return render_template("profile.html", deletable=deletable, claimable=claimable, claimables=claimables, vote=vote,data=datadict, kills=kills, friendships=friendships, others=other_saves, error=error, processtime=round(time.time()-start_time,5))


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
            db = connect_db()
            cur = db.cursor()
            cur.execute('SELECT id, md5, del_token, url FROM playerinfo WHERE owner_id IS NULL AND url IN '+app.sqlesc,(urls,))
            result = cur.fetchall()
            checked_results = []
            for row in result:
                if row[1] == session[row[3]] and row[2] == session[row[3]+'del_token']:
                    checked_results.append((row[0],row[3]))
            g.claimables = checked_results
            db.close()
        else:
            g.claimables = []
    return g.claimables


@profile.route('/<url>/<instruction>',methods=['GET','POST'])
def operate_on_url(url,instruction):
    error = None
    start_time = time.time()
    if request.method == 'POST':
        if (url in session and url+'del_token' in session) or logged_in():
            g.db = connect_db()
            cur = g.db.cursor()
            if logged_in():
                cur.execute('SELECT url,md5,del_token FROM playerinfo WHERE owner_id='+app.sqlesc,(get_logged_in_user(),))
                result = cur.fetchall()
                for row in result:
                    if not row[0] in session:
                        session[row[0]]=row[1]
                    if not row[0]+'del_token' in session:
                        session[row[0]+'del_token']=row[2]
            if instruction == 'del':
                cur.execute('SELECT owner_id FROM playerinfo WHERE url='+app.sqlesc,(url,))
                data = cur.fetchone()
                if str(data[0]) == str(get_logged_in_user()):
                    outcome = delete_playerinfo_entry(url,session[url],session[url+'del_token'])
                    if outcome == True:
                        return redirect(url_for('home'))
                    else:
                        error = outcome
                else:
                    error = 'You do not own this farm'
                return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))

            elif instruction == 'delall':
                cur.execute('SELECT url,owner_id FROM playerinfo WHERE series_id=(SELECT series_id FROM playerinfo WHERE url='+app.sqlesc+')',(url,))
                data = cur.fetchall()
                for row in data:
                    if str(row[1]) != str(get_logged_in_user()):
                        error = 'You do not own at least one of the farms'
                        return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
                # verified logged_in_user owns all farms
                for row in data:
                    outcome = delete_playerinfo_entry(row[0],session[row[0]],session[row[0]+'del_token'])
                    if outcome != True:
                        error = outcome
                        return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
                return redirect(url_for('home'))

            elif instruction == 'claim':
                if url in [url for rowid, url in find_claimables()]:
                    outcome = claim_playerinfo_entry(url,session[url],session[url+'del_token'])
                    if outcome == True:
                        return redirect(url_for('display_data',url=url))
                    else:
                        error = outcome
                else:
                    error = 'You do not have sufficient credentials to claim this page'
                return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))

            elif instruction == 'claimall':
                for rowid, claim_url in find_claimables():
                    outcome = claim_playerinfo_entry(claim_url,session[claim_url],session[claim_url+'del_token'])
                    if outcome != True:
                        error = 'You do not have sufficient credentials to claim one of these pages'
                return redirect(url_for('display_data',url=url))

            elif instruction == 'enable-dl':
                cur.execute('SELECT owner_id,id FROM playerinfo WHERE url='+app.sqlesc,(url,))
                data = cur.fetchone()
                if str(data[0]) == str(get_logged_in_user()):
                    cur = g.db.cursor()
                    cur.execute('UPDATE playerinfo SET download_enabled=TRUE WHERE id='+app.sqlesc,(data[1],))
                    g.db.commit()
                    return redirect(url_for('display_data',url=url))
                else:
                    error = 'You do not have sufficient credentials to perform this action'
                    return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))

            elif instruction == 'disable-dl':
                cur.execute('SELECT owner_id,id FROM playerinfo WHERE url='+app.sqlesc,(url,))
                data = cur.fetchone()
                if str(data[0]) == str(get_logged_in_user()):
                    cur = g.db.cursor()
                    cur.execute('UPDATE playerinfo SET download_enabled=FALSE WHERE id='+app.sqlesc,(data[1],))
                    g.db.commit()
                    return redirect(url_for('display_data',url=url))
                else:
                    error = 'You do not have sufficient credentials to perform this action'
                    return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))

            elif instruction == 'imgur':
                if logged_in():
                    check_access = imgur.checkApiAccess(get_logged_in_user())
                    if check_access == True:
                        result = imgur.uploadToImgur(get_logged_in_user(),url)
                        if 'success' in result:
                            return redirect(result['link'])
                        elif 'error' in result:
                            if result['error'] == 'too_soon':
                                error = 'You have uploaded this page to imgur in the last 2 hours: please wait to upload again'
                            elif result['error'] == 'upload_issue':
                                error = 'There was an issue with uploading the file to imgur. Please try again later!'
                        else:
                            error = 'There was an unknown error!'
                        return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
                    elif check_access == False:
                        return redirect(imgur.getAuthUrl(get_logged_in_user(),target=request.path))
                    elif check_access == None:
                        error = 'Either you or upload.farm are out of imgur credits for the day! Sorry :( Try again tomorrow'
                        return render_template("error.html", error=error, processtime=round(time.time()-start_time,5))
                else:
                    error = "You must be logged in to post your farm to imgur!"
                    return render_template("signup.html", error=error, processtime=round(time.time()-start_time,5))
        else:
            return render_template("error.html", error="Unknown instruction or insufficient credentials", processtime=round(time.time()-start_time,5))
    else:
        return redirect(url_for('display_data',url=url))


def delete_playerinfo_entry(url,md5,del_token):
    # takes url, md5, and del_token (from session); if verified, deletes
    g.db = connect_db()
    cur = g.db.cursor()
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
        g.db.commit()
        session.pop(url, None)
        session.pop(url+'del_token', None)
        return True
    else:
        return 'You do not have the correct session information to perform this action!'


def remove_series_link(rowid, series_id):
    # removes a link to playerinfo id (rowid) from id in series (series_id)
    if not hasattr(g,'db'):
        g.db = connect_db()
    cur = g.db.cursor()
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
    g.db.commit()
    return True


def claim_playerinfo_entry(url,md5,del_token):
    # verify ability to be owner, then remove_series_link (checking ownership!), then add_to_series
    if logged_in():
        if not hasattr(g,'db'):
            g.db = connect_db()
        cur = g.db.cursor()
        cur.execute('SELECT id,series_id,md5,del_token,owner_id,uniqueIDForThisGame,name,farmName FROM playerinfo WHERE url='+app.sqlesc,(url,))
        result = cur.fetchone()
        if result[2] == md5 and result[3] == del_token and result[4] == None:
            remove_series_link(result[0], result[1])
            series_id = add_to_series(result[0],result[5],result[6],result[7])
            cur.execute('UPDATE playerinfo SET series_id='+app.sqlesc+', owner_id='+app.sqlesc+' WHERE id='+app.sqlesc,(series_id,get_logged_in_user(),result[0]))
            g.db.commit()
            return True
        else:
            return 'Problem authenticating!'
    else:
        return 'You are not logged in!'


@profile.route('/_vote',methods=['POST'])
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
        g.db = connect_db()
        cur = g.db.cursor()
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
        g.db.commit()
        return True     
        # 4: commit, return


def has_votes(logged_in_user):
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('SELECT votes FROM users WHERE id='+app.sqlesc,(logged_in_user,))
    votes = cur.fetchone()[0]
    votes = json.loads(votes) if votes != None else {}
    return votes


def get_votes(url):
    if logged_in():
        result = has_votes(get_logged_in_user())
        return result[url] if url in result else None
    else:
        return None
