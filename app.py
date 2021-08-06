from re import M, split
from flask import Flask, redirect, flash, render_template, json, jsonify, make_response, request, current_app as app
from datetime import date, datetime, time
import os
import time
import flask_login
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import requests
import sqlite3 as sql
import urllib.request
from werkzeug.utils import secure_filename
import datetime
from flask_mail import Mail, Message
import string, random
import pusher

pusher_client = pusher.Pusher(
  app_id='1214298',
  key='a5fb9bca92914681546d',
  secret='5afbf42c792c68cefdae',
  cluster='us2',
  ssl=True
)

PROFILE_FOLDER = 'static/profile/'
POSTS_FOLDER = 'static/posts/'

today = date.today()
timeNow = time.strftime("%H:%M:%S")
# date = datetime.datetime.now()


def getName(email):

    if email == None:
        email = current_user.get_id()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT fname FROM users WHERE email='"+email+"'")
        fname = cur.fetchall()[0][0]
        con.commit()
        cur.close()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT lname FROM users WHERE email='"+email+"'")
        lname = cur.fetchall()[0][0]


        full_name = fname + " " + lname
        con.commit()
        cur.close()
    else:
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT fname FROM users WHERE email='"+email+"'")
        fname = cur.fetchall()[0][0]
        con.commit()
        cur.close()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT lname FROM users WHERE email='"+email+"'")
        lname = cur.fetchall()[0][0]


        full_name = fname + " " + lname
        con.commit()
        cur.close()

    return full_name

def getID(email):

    if email == None:
        email = current_user.get_id()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT userID FROM users WHERE email='"+email+"'")
        usID = cur.fetchall()[0][0]
        con.commit()
        cur.close()

    else:
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT userID FROM users WHERE email='"+email+"'")

        usID = cur.fetchall()[0][0]
        con.commit()
        cur.close()

    return usID

def getFriends(email):

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM friendships WHERE party1='"+email+"' OR party2='"+email+"'")

    friends = len(cur.fetchall())
    con.commit()
    cur.close()

    return friends

def getMessages(email):

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM all_messages WHERE email1='"+email+"' OR email2='"+email+"'")

    msgs = len(cur.fetchall())
    con.commit()
    cur.close()

    return msgs

def getEmail(ide):
    
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE userID="+ide+"")
    email = cur.fetchall()[0][0]
    con.commit()
    cur.close()

    return email

def getProf(email):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT profilePic FROM users WHERE email='"+email+"'")
    profPic = cur.fetchall()[0][0]
    con.commit()
    cur.close()

    return profPic


def getTime(y):
    today = date.today()
    timeNow = time.strftime("%H:%M:%S")
    when = ""
    x = str(y).split(" ")
    stoday = str(today)
    year = x[0].split("-")[0]
    month = x[0].split("-")[1]
    day = x[0].split("-")[2]
    if x[0] == stoday:
        hour = x[1].split(":")[0]
        minu = x[1].split(":")[1]
        seco = x[1].split(":")[2].split(".")[0]
        totime = ((int(timeNow.split(":")[0])*3600)+(int(timeNow.split(":")[1])*60)+int(timeNow.split(":")[2]))-((int(hour)*3600)+(int(minu)*60)+int(seco))
        if timeNow.split(":")[0] == hour or (int(timeNow.split(":")[0]) - int(hour)) == 1:
            if timeNow.split(":")[1] == minu:
                when = str(round(totime))+" second(s) ago"
            elif int(timeNow.split(":")[1])-int(minu) == 1 and int(timeNow.split(":")[2]) < 50:
                when = str(round(totime))+" second(s) ago"
            else:
                when = str(round(totime/60))+" minute(s) ago"
        else:
            when = str(round(totime/3600))+" hours ago"
    elif stoday.split("-")[0] == year:
        if stoday.split("-")[1] == month:
            when = str(int(stoday.split("-")[2])-int(day))+" day(s) ago"
        elif int(stoday.split("-")[1])-int(month) == 1 and int(stoday.split("-")[2]) < 24:
            when = str(int(stoday.split("-")[2]))+" day(s) ago"
        else:
            when = str(int(stoday.split("-")[1])-int(month))+" month(s) ago"
    else:
        when = str(int(stoday.split("-")[0])-int(year))+" year(s) ago"
    
    return when

app = Flask(__name__, static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hootsservice@gmail.com'
app.config['MAIL_PASSWORD'] = 'hootytoot'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def resetPassword(email,tempPass):
    msg = Message('Hello', sender = 'hootsservice@gmail.com', recipients = [email])
    msg.body = "Hello Hoots user, your password has been set to the following temporary password please login and change as you please. __"+tempPass+"__"
    mail.send(msg)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self,email):
         self.email = email
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.email

@login_manager.user_loader
def load_user(user_id):
   conn = sql.connect('./static/data/data.db')
   curs = conn.cursor()
   curs.execute("SELECT * from users where email = (?)",[user_id])
   lu = curs.fetchone()
   if lu is None:
      return None
   else:
      return User(lu[2])

con = sql.connect("./static/data/data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password" TEXT, "profilePic" TEXT, "bio" TEXT, "username" TEXT, "security question" TEXT, "security answer" TEXT, "userID" INTEGER PRIMARY KEY)')
cur.execute('CREATE TABLE IF NOT EXISTS "followers" ("follower" TEXT,"following" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "friendships" ("party1" TEXT,"party2" TEXT,"accepted" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_posts" ("post" TEXT, "title" TEXT, "date" TEXT, "name" TEXT, "description" TEXT, "likes" TEXT, "likesAmount" INTEGER, "comments" INTEGER, "email" TEXT, "profilePic" TEXT, "day" TEXT, "type" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_comments" ("id", "name", "comment", "date", "email", "profilePic")')
cur.execute('CREATE TABLE IF NOT EXISTS "message_group" ("rowID" INTEGER PRIMARY KEY, "email1", "email2", "date")')
cur.execute('CREATE TABLE IF NOT EXISTS "all_messages" ("groupID" , "email1", "email2", "message", "date", type)')

con.commit()
cur.close()

app.secret_key = "secret key"
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER
app.config['POSTS_FOLDER'] = POSTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1080 * 1080

full_name = ""
change = ""
defPic = "data:image/jpeg;base64,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"

tempPosts = []
postsDB = ""
posts = 0
tempComments = []
commentsDB = ""
comments = 0
def reloadDB():

    global tempPosts
    global postsDB
    global posts
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    tempPosts = []
    for row in reversed(rows):
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],getTime(row[2]),getID(row[8]),row[11]]
        tempPosts.append(post)
    cur.close()
    postsDB = tempPosts  # The mock database
    posts = len(tempPosts)  # num posts to generate

    global tempComments
    global commentsDB
    global comments

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT * from all_comments")
    rows = cur.fetchall()
    tempComments = []
    for row in rows:
        comment = [row[0],row[1],row[2],getTime(row[3]),row[4],row[5]]
        tempComments.append(comment)
    cur.close()
    commentsDB = tempComments  # The mock database
    comments = len(tempComments)  # num posts to generate

reloadDB()

quantity = 5  # num posts to return per request

@app.before_request
def before_request():
    reloadDB()
    # app.logger.info("before_request")

@app.route("/load")
def load():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    if request.args:
        counter = int(request.args.get("c"))  # The 'counter' value sent in the QS

        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
            # Slice 0 -> quantity from the db
            res = make_response(jsonify(postsDB[0: quantity]), 200)

        elif counter == posts:
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            # Slice counter -> quantity from the db
            res = make_response(jsonify(postsDB[counter: counter + quantity]), 200)
    
    return res

@app.route("/load2")
def load2():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    if request.args:
        counter = int(request.args.get("c"))  # The 'counter' value sent in the QS

        # Slice counter -> quantity from the db
        res = make_response(jsonify(commentsDB[counter: len(commentsDB)]), 200)
    
    return res


postsDB2 = []
@app.route("/load3")
def load3():
    """ Route to return the posts """

    time.sleep(0.2)  # Used to simulate delay

    if request.args:
        counter = int(request.args.get("c"))  # The 'counter' value sent in the QS

        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
            # Slice 0 -> quantity from the db
            res = make_response(jsonify(postsDB2[0: quantity]), 200)

        elif counter == posts:
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            # Slice counter -> quantity from the db
            res = make_response(jsonify(postsDB2[counter: counter + quantity]), 200)
    
    return res

@app.route('/')
def index():

    if current_user.get_id() != None:

        return  redirect("/home", code=302)

    return render_template('index.html')


@app.route('/friends/<friend>')
def friend(friend):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()
    friends_already = False

    cur.execute('SELECT * FROM friendships WHERE (party1="'+email+'" AND party2="'+friend+'") OR (party2="'+email+'" AND party1="'+friend+'")')
    friends = cur.fetchall()
    for thing in friends:
        if thing[0] == email:
            if thing[1] == friend:
                friends_already = True

        if thing[1] == email:
            if thing[0] == friend:
                friends_already = True


    if friends_already == False:
        cur.execute("INSERT INTO friendships(party1, party2, accepted) VALUES((?),(?),(?))", (email,friend,"False"))
        con.commit()
        con.close()
    else:
        cur.execute("DELETE FROM friendships WHERE (party1='"+email+"' AND party2='"+friend+"') OR (party2='"+email+"' AND party1='"+friend+"')")
        con.commit()
        con.close()


    return redirect('/friends')

@app.route('/delete/<friend>')
def delete(friend):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()
    friends_already = False

    cur.execute("DELETE FROM friendships WHERE (party1='"+email+"' AND party2='"+friend+"') OR (party2='"+email+"' AND party1='"+friend+"')")
    con.commit()
    con.close()


    return redirect('/friends')

@app.route('/accept/<friend>')
def accept(friend):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()
    friends_already = False

    cur.execute("UPDATE friendships SET accepted = 'True' WHERE (party1='"+email+"' AND party2='"+friend+"') OR (party2='"+email+"' AND party1='"+friend+"')")
    con.commit()
    con.close()


    return redirect('/friends')



@app.route('/friends')
def friends():
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()

    cur.execute('SELECT * FROM friendships WHERE party1="'+email+'" OR party2="'+email+'"')
    friends_list = cur.fetchall()
    con.commit()
    con.close()
    list = []
    list_of_friends = []
  
    for friends in friends_list:
        if friends[2] == "False":

            friend = [friends[0],friends[1]]
            if friends[1] == email:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                pic_sql = 'SELECT profilePic FROM users WHERE email=?'
                cur.execute(pic_sql, (friend[1],))
                pic = cur.fetchall()
                pic = pic[0][0]
                message = [getName(friend[0]),pic,friend[0]]
                con.commit()
                con.close()
                list.append(message)
        else:
            friend = [friends[0],friends[1]]
            if friends[0] == email:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                pic_sql = 'SELECT profilePic FROM users WHERE email=?'
                cur.execute(pic_sql, (friend[1],))
                pic = cur.fetchall()
                pic = pic[0][0]
                mes = [getName(friend[1]),pic,friend[1]]
                con.commit()
                con.close()
                list_of_friends.append(mes)
                
            else:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                pic_sql = 'SELECT profilePic FROM users WHERE email=?'
                cur.execute(pic_sql, (friend[0],))
                pic = cur.fetchall()
                pic = pic[0][0]
                mes = [getName(friend[0]),pic,friend[0]]
                con.commit()
                con.close()
                list_of_friends.append(mes)

            

    return render_template('friends.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), list = list, email = email ,flist = list_of_friends)

@app.route('/messages/<friend>')
@login_required
def addmessage(friend):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()
    group_already = False

    cur.execute('SELECT * FROM message_group WHERE (email1="'+email+'") OR (email2="'+email+'")')
    friends = cur.fetchall()
    for thing in friends:
        if thing[1] == email:
            if thing[2] == friend:
                group_already = True

        if thing[2] == email:
            if thing[1] == friend:
                group_already = True


    if group_already == False:
        cur.execute("INSERT INTO message_group(email1, email2) VALUES((?),(?))", (email,friend))
        con.commit()
        con.close()
    else:
        # cur.execute("DELETE FROM message_group WHERE (email1='"+email+"' AND email2='"+friend+"') OR (email1='"+email+"' AND email2='"+friend+"')")
        # con.commit()
        # con.close()
        ""
    

    return redirect("/messages", code=302)

@app.route('/profile')
@login_required
def profile():
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    email = current_user.get_id()

    pic_sql = 'SELECT profilePic FROM users WHERE email=?'
    cur.execute(pic_sql, (email,))
    pic = cur.fetchall()
    pic = pic[0][0]

    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()
    lname = lname[0][0]

    cur.execute('SELECT * FROM all_posts WHERE email="'+email +'"')
    posts = cur.fetchall()
    post_num = len(posts)

    cur.execute('SELECT * FROM followers WHERE following="'+email +'"')
    follow = cur.fetchall()
    followersAmt = len(follow)

    cur.execute('SELECT * FROM friendships WHERE party1="'+email +'" OR party2="'+email+'"')
    friendl = cur.fetchall()
    friendAmt = len(friendl)

    name = fname + " " + lname

    return render_template('profile.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), email=email, pic = pic, name = name, post_num = post_num, followers=followersAmt, friends=friendAmt)

@app.route('/profile/<email>')
@login_required
def profile2(email):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT email FROM users WHERE userID="'+email+'"')
    email = cur.fetchall()[0][0]

    email2 = current_user.get_id()
    #check if email exists

    follows = "Follow+"
    cur.execute('SELECT following FROM followers WHERE following="'+email+'"')
    followings = cur.fetchall()
    for follower in followings:
        if follower[0] == email:
            follows = "UnFollow"

    friendo = "+Friend"
    cur.execute('SELECT * FROM friendships WHERE party1="'+email+'" OR party2="'+email+'"')
    friendings = cur.fetchall()
    for friendy in friendings:
        if friendy[0] == email and friendy[1] == email2:
            friendo = "UnFriend"
        if friendy[1] == email and friendy[0] == email2:
            friendo = "UnFriend"

    pic_sql = 'SELECT profilePic FROM users WHERE email=?'
    cur.execute(pic_sql, (email,))
    pic = cur.fetchall()
    if pic[0][0]:
        pic = pic[0][0]
    else:
        pic = ""

    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()
    lname = lname[0][0]

    cur.execute('SELECT * FROM all_posts WHERE email="'+email +'"')
    posts = cur.fetchall()
    post_num = len(posts)

    cur.execute('SELECT * FROM followers WHERE following="'+email +'"')
    follow = cur.fetchall()
    followersAmt = len(follow)

    cur.execute('SELECT * FROM friendships WHERE party1="'+email +'" OR party2="'+email+'"')
    friendl = cur.fetchall()
    friendAmt = len(friendl)

    name = fname + " " + lname

    return render_template('profile.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), email=email, pic = pic, name = name, post_num = post_num, followers=followersAmt, follows=follows, isProf="no", friends=friendAmt, friendo=friendo)

@app.route('/messages')
@login_required
def messages2():

    email = current_user.get_id()
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    msg = ""

    cur.execute('SELECT * FROM message_group WHERE (email1="'+email+'") OR (email2="'+email+'")')
    bob = cur.fetchall()

    messageGroup = []
    for row in bob:
        if email != row[2]:
         ppl = [row[1],row[2],getName(row[2]),getID(row[2]),row[3],getProf(row[2])]
        else:
         ppl = [row[1],row[2],getName(row[1]),getID(row[1]),row[3],getProf(row[1])]
        messageGroup.append(ppl)
        
    cur.close()
    con.close()

    return render_template('messages.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), messageGroup = messageGroup)

@app.route('/sendMessage/<reciever>/<msg>', methods=["POST","GET"])
def messageSEND(reciever,msg):

    email = current_user.get_id()
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    ol = reciever

    sqle = 'SELECT email FROM users WHERE userID=?'
    cur.execute(sqle, (reciever,))
    sname = cur.fetchall()
    reciever = sname[0][0]
    msg2=""

    sqle2 = 'SELECT rowID FROM message_group WHERE (email1=? AND email2=?) OR (email2=? AND email1=?)'
    cur.execute(sqle2, (reciever,email,reciever,email))
    sname2 = cur.fetchall()
    groupID = sname2[0][0]
    day = today.strftime("%B %d, %Y")
    date = str(datetime.datetime.now())
    toim = ""
    type = ""
    img = request.files['img']
    print(img)
    imgname = img.filename
    if img.filename != "":
        imgname = imgname.replace(" ","_")
        filename = secure_filename(imgname)
        img.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        msg2 = imgname
        type="img"

        flash('Image successfully uploaded and displayed below')

    vid = request.files['vid']
    print(vid)
    if vid.filename != "":
        vidname = vid.filename
        vidname = vidname.replace(" ","_")
        filename = secure_filename(vidname)
        vid.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        msg2 = vidname
        type="vid"

        flash('Image successfully uploaded and displayed below')

    if int(date.split(" ")[1].split(":")[0]) > 12:
        toim = str(int(date.split(" ")[1].split(":")[0])-12)+":"+str(date.split(" ")[1].split(":")[1])+"pm"
    else:
        toim = str(int(date.split(" ")[1].split(":")[0]))+":"+str(date.split(" ")[1].split(":")[1])+"am"

    if type!="":
        cur.execute("INSERT INTO all_messages(groupID ,email1, email2, message, date, type) VALUES((?),(?),(?),(?),(?),(?))", (groupID,email,reciever,msg2,day+" at "+toim,type))
    if msg!="SECRETCODEkjadnfjasdnfnsadfnaksdkflnsdamfklasdmfklsdamfaksdmfnlsadfa":
        cur.execute("INSERT INTO all_messages(groupID ,email1, email2, message, date, type) VALUES((?),(?),(?),(?),(?),(?))", (groupID,email,reciever,msg,day+" at "+toim,""))
    con.commit()
    con.close()

    pusher_client.trigger('msg-channel', 'new-message', {'userID': ol, 'message': msg, 'time': 'Today at '+toim})

    return ""

@app.route('/message/<reciever>')
def messages(reciever):
    
    email = current_user.get_id()
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    friend = getEmail(reciever)
    cur.execute('SELECT * FROM message_group WHERE (email1="'+email+'") OR (email2="'+email+'")')
    bob = cur.fetchall()

    messageGroup = []
    for row in bob:
        if email != row[2]:
         ppl = [row[1],row[2],getName(row[2]),getID(row[2]),row[3],getProf(row[2])]
        else:
         ppl = [row[1],row[2],getName(row[1]),getID(row[1]),row[3],getProf(row[1])]
        messageGroup.append(ppl)

    cur.execute('SELECT * FROM all_messages WHERE (email1="'+email+'" AND email2="'+getEmail(reciever)+'") OR (email2="'+email+'" AND email1="'+getEmail(reciever)+'")')
    bob = cur.fetchall()

    messages = []
    for row in bob:
        if email==row[2]:
         today = date.today().strftime("%B %d %Y")
         if row[4].split(" ")[0]+" "+row[4].split(" ")[1].split(",")[0]+" "+row[4].split(" ")[2] == today:
             newrow = "Today at "+row[4].split(" ")[4]
         else:
             newrow = row[4]
         msg = [1,row[3],newrow,row[5]]
        else:
         today = date.today().strftime("%B %d %Y")
         if row[4].split(" ")[0]+" "+row[4].split(" ")[1].split(",")[0]+" "+row[4].split(" ")[2] == today:
             newrow = "Today at "+row[4].split(" ")[4]
         else:
             newrow = row[4]
         msg = [2,row[3],newrow,row[5]]
        messages.append(msg)
    ml = getID(email)
    ol = reciever
    gic = getProf(getEmail(ol))
    sqle = 'SELECT email FROM users WHERE userID=?'
    cur.execute(sqle, (reciever,))
    sname = cur.fetchall()
    reciever = sname[0][0]

    return render_template('messages.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), messageGroup=messageGroup, reciever = reciever, messages = messages, ol=ol, theName = getName(reciever), gic=gic, ml=ml)

@app.route('/settings')
@login_required
def settings():

    full_name = getName(None)
    global change
    changed = change
    change = ""

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users WHERE email="'+current_user.get_id()+'"')

    all = cur.fetchall()

    users = []

    for row in all:
        users.append(row[4])

    pic = users[0]
    print(pic)

    cur.close()
    con.close()

    return render_template('settings.html',  full_name = full_name, match = False, ematch = False, change=changed, pic=pic)

@app.route('/ForgotPassword')
def forgotPassword():
    if current_user.get_id() != None:

        return  redirect("/home", code=302)

    return render_template("change.html",info="Enter your email address associated with the account:")

@app.route('/ForgotPassword/<email>')
def forgotPassword2(email):
    if current_user.get_id() != None:

        return  redirect("/home", code=302)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT email FROM users")

    emails = cur.fetchall()

    for row in emails:
        if row[0].upper() == email.upper():
            tempPass = ""
            for i in range(12):
                r  = random.choice(string.ascii_letters)
                tempPass = tempPass+r
            con = sql.connect("./static/data/data.db")
            cur = con.cursor()
            cur.execute("UPDATE users SET password='"+tempPass+"' WHERE email='"+email+"'")
            con.commit()
            cur.close()
            resetPassword(email,tempPass)
            return render_template("change.html", info = "A change password email has been sent to "+email)

    cur.close()
    con.close()
    return render_template("change.html", info = "Email does not exists please enter the correct email address associated with the account:")

@app.route('/home')
@login_required
def home():

    full_name = getName(None)

    stock_key = "9J76BVB2N976KTZN"
    
    profilePic = []

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()

    users = []

    for row in all:
        users.append(row[4])

    cur.close()
    con.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT profilePic,email from users")
    pic = cur.fetchall()
    for row in pic:
        profilePic.append(row)

    email = current_user.get_id()


    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],getTime(row[2]),getID(row[8])]
        posts.append(post)
    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT * from all_comments")
    rowes = cur.fetchall()
    comments = []
    for row in rowes:
        comment = [row[0],row[1],row[2],row[3],row[4],row[5]]
        comments.append(comment)
    cur.close()

    use_key = False
    
    r = requests.get('https://api.ipdata.co?api-key=efa9939867be7cb086c0afd1ddbb716005e0efcea4f4313d6d130842').json()
    place = r['city']

    minimum_value = 12
    maximum_value = 40
    daily_headline = "not using key"
    new_num = 16

    if use_key == True:
        weather_key = "tGTXQE1y2fZmVzxcOgn5gO4gZHYw6pvP"

        key_link = requests.get("https://dataservice.accuweather.com/locations/v1/cities/search?apikey=" + weather_key + "&q=" + place).json()
        key = key_link[0]['Key']

        complete_api_link = "https://dataservice.accuweather.com/forecasts/v1/daily/1day/" + key + "?apikey=" + weather_key
        print(complete_api_link)

        api_link = requests.get(complete_api_link)
        api_data = api_link.json()
        minimum_value = api_data['DailyForecasts'][0]['Temperature']['Minimum']['Value']
        maximum_value = api_data['DailyForecasts'][0]['Temperature']['Maximum']['Value']
        daily_headline = api_data['Headline']['Text']
        iconNum = api_data['DailyForecasts'][0]['Day']['Icon']
        print(type(iconNum))
        new_num = iconNum
        if iconNum < 10:
            new_num = str(iconNum).zfill(2)
        else:
            new_num = str(iconNum)
    


    #504613a92ad54b5ab541958334451484

    articles = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=504613a92ad54b5ab541958334451484').json()
    title = articles['articles'][0]['title']
    desc = articles['articles'][0]['description']
    image = articles['articles'][0]['urlToImage']
    url = articles['articles'][0]['url']
    


    all_articles = []
    all = articles['articles']
    for i in all:
      thing = [i['title'], i['description'],i['urlToImage'],i['url'],i['source']['name']]
      all_articles.append(thing)

    quote_link = requests.get('https://zenquotes.io/api/random').json()
    quote = quote_link[0]['q']
    author = quote_link[0]['a']
    h = quote_link[0]['h']

    return render_template('home.html', users=users, posts = posts, comments=comments, replies="replies", name=full_name, email=current_user.get_id(), profilePic = profilePic, min = minimum_value, max = maximum_value, head = daily_headline, i_num = new_num, title = title, image = image, url = url, desc = desc, articles = all_articles, q = quote, a = author, h = h,place=place)

@app.route('/search' , methods=['GET', 'POST'])
@login_required
def search():

    full_name = getName(None)

    search = request.form.get('search')
    print(search)
   


    profilePic = []

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()

    users = []

    for row in all:
        users.append(row[4])

    cur.close()
    con.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT profilePic,email from users")
    pic = cur.fetchall()
    for row in pic:
        profilePic.append(row)

    email = current_user.get_id()


    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    
    
   
    
    cur.execute("SELECT * FROM all_posts WHERE name LIKE '" + "%" +search+ "%" + "'")
    
    rows = cur.fetchall()
    
    global postsDB2
    postsDB2 = []
    for row in reversed(rows):
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],getTime(row[2]),getID(row[8]),row[11]]
        postsDB2.append(post)
    cur.close()




    # cur.execute("SELECT * FROM all_posts WHERE name LIKE '" + "%" +search+ "%" + "'")
    
    # rows = cur.fetchall()
    
    # global postsDB2
    # postsDB2 = []
    # for row in reversed(rows):
    #     post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],getTime(row[2]),getID(row[8]),row[11]]
    #     postsDB2.append(post)
    # cur.close()


    # cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password" TEXT, "profilePic" TEXT, "bio" TEXT, "username" TEXT, "security question" TEXT, "security answer" TEXT, "userID" INTEGER PRIMARY KEY)')
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT * FROM users WHERE fname LIKE '" + "%" +search+ "%" + "' OR lname LIKE '" + "%" +search+ "%" + "'")

    profile_rows = cur.fetchall()

    profiles = []

    for row in profile_rows:
        name = row[0] + " " + row[1]
        profile = [name, row[2],row[4],getID(row[2])]
        print(profile)
        profiles.append(profile)

    # pic_sql = 'SELECT profilePic FROM users WHERE email=?'
    # cur.execute(pic_sql, (email,))
    # pic = cur.fetchall()
    # pic = pic[0][0]

    # fname_sql = 'SELECT fname FROM users WHERE email=?'
    # cur.execute(fname_sql, (email,))
    # fname = cur.fetchall()
    # fname = fname[0][0]

    # lname_sql = 'SELECT lname FROM users WHERE email=?'
    # cur.execute(lname_sql, (email,))
    # lname = cur.fetchall()
    # lname = lname[0][0]



    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT * from all_comments")
    rows = cur.fetchall()
    comments = []
    for row in rows:
        comment = [row[0],row[1],row[2],row[3],row[4],row[5]]
        comments.append(comment)
    cur.close()
   
    return render_template('search.html', users=users, posts = postsDB, comments=comments, replies="replies", name=full_name, email=current_user.get_id(), profilePic = profilePic, profiles = profiles)

@app.route('/home/post')
@login_required
def homePost():


    full_name = getName(None)
    email = current_user.get_id()



    return render_template('posts.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), type=type)

@app.route('/post', methods=['GET', 'POST'])
def post():


    full_name = getName(None)
    email = getID(current_user.get_id())

    postName = ""

    type = "img"

    img = request.files['img']
    imgname = img.filename
    if img.filename != "":
        imgname = imgname.replace(" ","_")
        filename = secure_filename(imgname)
        img.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        postName = imgname

        flash('Image successfully uploaded and displayed below')

    vid = request.files['vid']
    if vid.filename != "":
        vidname = vid.filename
        vidname = vidname.replace(" ","_")
        filename = secure_filename(vidname)
        vid.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        postName = vidname
        type="vid"

        flash('Image successfully uploaded and displayed below')



    title = request.form.get("title", False)
    description = request.form.get("description", False)
    day = today.strftime("%B %d, %Y")
    date = datetime.datetime.now()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT profilePic FROM users WHERE email='"+current_user.get_id()+"'")
    profPic = cur.fetchall()[0][0]
    con.commit()
    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email, profilePic, day, type) VALUES((?),(?),(?),(?),(?),(?),(?),(?),(?),(?),(?),(?))", (postName, title, date, full_name, description, "[]", 0, 0, current_user.get_id(), profPic, day,type))
    #cur.execute("INSERT INTO " + email.upper() + "(post, name) VALUES((?),(?))", (post, full_name))
    #cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email) VALUES((?),(?))", (post, full_name))
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]]
        posts.append(post)

    con.commit()
    con.close()


    return redirect("/home", code=302)

@app.route('/change_pic',methods = ['POST', 'GET'])
@login_required
def profilePic():


    full_name = getName(None)
    email = current_user.get_id()
    global change
    img = request.files['prof']
    imgname = img.filename
    if img.filename != "":

        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['PROFILE_FOLDER'], filename))

        flash('Image successfully uploaded and displayed below')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("UPDATE users SET profilePic = '"+imgname+"' WHERE email='"+email+"'")
    cur.execute("UPDATE all_posts SET profilePic='"+imgname+"' WHERE email='"+email+"'")
    cur.execute("UPDATE all_comments SET profilePic='"+imgname+"' WHERE email='"+email+"'")

    con.commit()
   

    change = "PROFILE PIC CHANGED SUCCESSFULLY!"

    return redirect('/settings', code=302)

@app.route('/register',methods = ['POST', 'GET'])
def register():
    global defPic



    fname = request.form.get('fname', False)
    lname = request.form.get('lname', False)
    email = request.form.get('email', False)
    password = request.form.get('password', False)

    full_name = fname + " " + lname
    insert = '"' + email + '"'

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT email FROM users')

    emails = cur.fetchall()

    huh = "EMAIL DO NOT EXIST"

    for row in emails:
        if row[0].upper() == email.upper():
            huh = "EMAIL EXISTS"
            print(huh)
            return render_template('index.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), failed2 = "Email already exists")

    if huh == "EMAIL DO NOT EXIST":
        print('hi')
        cur.execute("INSERT INTO users(fname, lname, email, password, profilePic) VALUES((?),(?),(?),(?),(?))", (fname, lname, email, password,defPic))
        cur.execute('CREATE TABLE' + insert  + '("post" TEXT, "name" TEXT)')
        


        con.commit()

    cur.close()
    con.close()

    Us = load_user(email)
    login_user(Us, remember = email)

    return redirect("/home", code=302)

@app.route('/login',methods = ['POST', 'GET'])
def login():

    name = ""
    email = request.form.get('email', False)
    password = request.form.get('password', False)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()

    exists = False

    for row in all:
        if email!=False:
            if row[2].upper() == email.upper():
                exists = True
                if row[3] == password:
                    name = row[0]


                    Us = load_user(email)
                    login_user(Us, remember = email)

                elif name != row[0]:
                    return render_template('index.html', failed = "Password is incorrect")

    if exists == False:
            return render_template('index.html',  failed = "Email is not registered")



    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()
    lname = lname[0][0]

    full_name = fname+" "+lname

    cur.close()
    con.close()

    return redirect("/home", code=302)


@app.route('/like/<id>',methods = ['POST', 'GET'])
@login_required
def like(id):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]]
        posts.append(post)
    cur.close()
    for post in posts:
        if id == post[2]:
            if ","+current_user.get_id() not in post[5]:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                cur.execute("UPDATE all_posts SET likesAmount=likesAmount+1 WHERE date='"+post[2]+"'")
                cur.execute("UPDATE all_posts SET likes=trim(',"+current_user.get_id()+"') WHERE date='"+post[2]+"'")
                con.commit()

                cur.close()
                con.close()
                return "successDrop"

            con = sql.connect("./static/data/data.db")
            cur = con.cursor()
            cur.execute("UPDATE all_posts SET likesAmount=likesAmount-1 WHERE date='"+post[2]+"'")
            cur.execute("UPDATE all_posts SET likes=likes+',"+current_user.get_id()+"' WHERE date='"+post[2]+"'")
            con.commit()

            cur.close()
            con.close()
    return "success", 200

@app.route('/follow/<following>',methods = ['POST', 'GET'])
@login_required
def follow(following):

    email = current_user.get_id()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    follows = "Follow+"
    cur.execute('SELECT following FROM followers WHERE following="'+following+'"')
    followings = cur.fetchall()
    for follower in followings:
        if follower[0] == email:
            follows = "UnFollow"

    if follows == "Follow+":
        cur.execute("INSERT INTO followers(follower,following) VALUES((?),(?))", (email,following))
        con.commit()
    if follows == "UnFollow":
        cur.execute("DELETE FROM followers WHERE follower='"+email+"' AND following='"+following+"'")
        con.commit()

    cur.close()
    con.close()

    return "success", 200

@app.route('/comment/<comment>/<id>/<prof>',methods = ['POST', 'GET'])
@login_required
def comments(comment,id,prof):

    full_name = getName(None)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    date = datetime.datetime.now()

    cur.execute("INSERT INTO all_comments(id, name, comment, date, email, profilePic) VALUES((?),(?),(?),(?),(?),(?))", (id, full_name, comment, date, current_user.get_id(), prof))
    cur.execute("UPDATE all_posts SET comments=comments+1 WHERE date='"+id+"'")
    con.commit()

    cur.close()
    con.close()

    return "success", 200

@app.route('/change_password', methods = ['POST', 'GET'])
@login_required
def change_pass():


    full_name = getName(None)


    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT password FROM users WHERE email='"+current_user.get_id()+"'")
    curent_password = cur.fetchall()
    curent_password = curent_password[0][0]
    print(curent_password)

    con.commit()
    cur.close()

    if(old_pass == curent_password):
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("UPDATE users SET password='"+new_pass+"' WHERE email='"+current_user.get_id()+"'")
        con.commit()
        cur.close()
        global change
        change = "PASSWORD CHANGED SUCCESSFULLY!"
        return redirect("/settings", code = 302)
    else:
        print('Not a match')
        match = True
        con.commit()
        cur.close()
        return render_template('settings.html', friendsNum = getFriends(current_user.get_id()), msgNum = getMessages(current_user.get_id()), full_name = full_name, exists = match, ematch = False)

@app.route('/change_email', methods = ['POST', 'GET'])
@login_required
def change_email():




    full_name = getName(None)

    new_email = request.form.get('new_email')



    con = sql.connect("./static/data/data.db")
    cur = con.cursor()


    cur.execute('SELECT email FROM users')

    emails = cur.fetchall()

    huh = "EMAIL DO NOT EXIST"

    exists = False

    for row in emails:
        if row[0].upper() == new_email.upper():
            huh = "EMAIL EXISTS"
            exists = True

    if huh == "EMAIL DO NOT EXIST":
        cur.execute("UPDATE users SET email='"+new_email+"' WHERE email='"+current_user.get_id()+"'")
        Us = load_user(new_email)
        login_user(Us, remember = new_email)
        exists = False
        con.commit()
        cur.close()
        global change
        change = "EMAIL CHANGED SUCCESSFULLY!"
        return redirect("/settings", code = 302)
    else:
        return render_template('settings.html', full_name = full_name, match = False, ematch = exists)

@app.route('/change_name', methods = ['POST', 'GET'])
@login_required
def change_name():

    full_name = getName(None)

    fname = request.form.get('fname')
    lname = request.form.get('lname')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET fname='"+fname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE users SET lname='"+lname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE all_posts SET name='"+fname+" "+lname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE all_comments SET name='"+fname+" "+lname+"' WHERE email='"+current_user.get_id()+"'")
    print("")
    full_name = fname + " " + lname
    con.commit()
    
    global change
    change = "NAME CHANGED SUCCESSFULLY!"
    return redirect("/settings", code = 302)

@app.route('/logout',methods = ['POST', 'GET'])
@login_required
def logout():

    logout_user()

    return redirect("/", code=302)




if __name__ == '__main__':
 app.run(threaded=True, debug=True, host='0.0.0.0')



 #this is just some random code for no reason
 


