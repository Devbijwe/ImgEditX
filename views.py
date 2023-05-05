from PIL import Image
import os
from werkzeug.utils import secure_filename
import random
import math
import json
from flask import Flask, make_response,render_template,abort,session,redirect,send_file, request,flash,jsonify,Response,url_for,abort
from jinja2 import Template
from datetime import datetime
import uuid                                                                                                                         
from flask_mail import Mail
import requests
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from requests.structures import CaseInsensitiveDict
from .__init__ import app,db
from .models import *

with open("config.json","r") as c:
    params=json.load(c)['params']
with open("config.json","r") as d:
    directories=json.load(d)['directories']

# *********************************


           
#  ***************************************Login and logout******************************************

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "982830238929-q9jhr9qk4bnps9abk5m5o5a34pdg068p.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:4000/callback"
)
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

@app.route("/login/auth/google")
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    # try:
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    # print(credentials)
    # return credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)

    token_request = google.auth.transport.requests.Request(session=cached_session)


    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    sub= id_info.get("sub")
    name = id_info.get("name")
    email = id_info.get("email")
    mobile = id_info.get("mobile")
    picture=id_info.get("picture")
    print(id_info)
    password=sub
    # return id_info
    user=Users.query.filter_by(email=email).first()
    
    if user is None:
        id = uuid.uuid4().hex
        cred=Users(id=id,name=name,mobile=mobile,email=email,password=password,picture=picture,date=datetime.now())
        try:
            db.session.add(cred)
            db.session.commit()
            mainstr="login"
            session["user"]=id
            return redirect("/google/auth") 
        except:
            flash("Some error occured please reload page")
    if user.picture is None:
        user.picture=picture
        db.session.commit()
    session["user"]=user.id
    # flash("Account already exists")
    return redirect("/login/auth")
    # except:
        
    #     return redirect("/login/auth")


# login and signups       
@app.route("/<string:mainstr>/auth",methods=['GET','POST'])
def login(mainstr):
    if mainstr not in ["login", "signup", "google"]:
        abort(404)
    if 'user' in session:
        mobile=request.form.get("mobile")
        password=request.form.get("password")
        if mainstr=="google":
            
            user=Users.query.filter_by(id=session['user']).first()
        if "redirect_to" in session:
            return redirect(session["redirect_to"]) 
         
        return redirect("/")
    elif mainstr=="whatsapp":
        mobile=request.form.get("mobile")
        password=request.form.get("password")
        name=request.form.get("name")
        user=Users.query.filter_by(mobile=mobile).first()
        
        if user:
            session['user']=user.id
            return {
                    "code":200,
                    "msg":"You logged in as %s" %name,
                    "redirect_url":"/login/auth"
                }
        else:
            id = uuid.uuid4().hex
            cred=Users(id=id,name=name,mobile=mobile,password=password,date=datetime.now())
            try:
                db.session.add(cred)
                db.session.commit()
                session['user']=id
                return {
                    "code":200,
                    "msg":"You logged in as %s" %name,
                    "redirect_url":"/login/auth"
                }
            except:
                flash("Some error occured please reload page")
            
            
    
        
            
        # user=Users.query.filter_by(id=session['user']).first()
        if "redirect_to" in session:
            return redirect(session["redirect_to"]) 
         
        return redirect("/")
            
          
    else:
        mobile=request.form.get("mobile")
        password=request.form.get("password")
        
        if request.method=="POST" and mainstr=="signup":
            name=request.form.get("username")
            email=request.form.get("email")
            # try:
            #     user=Users.query.filter_by(mobile=mobile).first()
            # except:
            #     user=Users.query.filter_by(email=mobile).first()
            user=Users.query.filter((Users.mobile == mobile) | (Users.email == email)).first()
                
            if user:
                flash("Account already exists!")
            else:
                id = uuid.uuid4().hex
                cred=Users(id=id,name=name,mobile=mobile,email=email,password=password,date=datetime.now())
                try:
                    db.session.add(cred)
                    db.session.commit()
                    mainstr="login"
                    session['user']=id
                    if "redirect_to" in session:
                        return redirect(session["redirect_to"])
                    else:  
                        
                        return redirect("/")
                except:
                    flash("Some error occured please reload page")
        elif request.method=="POST" and mainstr=="login":
            user=Users.query.filter((Users.mobile == mobile) | (Users.email == mobile)).first()
            print(password==user.password,password,user.password)
            if user and password==user.password:
                session['user']=user.id
                if "redirect_to" in session:
                    return redirect(session["redirect_to"])
                else:  
                     
                    return redirect("/")
                
            elif user and password!=user.password:
                flash("You have entered wrong password!")
            else:
                flash("Account doesn't exists!")
    
    return render_template("login.html", page=mainstr)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


#home page
@app.route("/",methods=['GET'])   
def home():
    session.permanent = True
    return render_template("index.html")


#  ************************************************************************************

# opens editor
# @app.route("/editor",methods=['GET'])
# def edits():
#     if 'user' in session:
#         return render_template("editor.html",url=None)
#     else:
#         session["redirect_to"]="/editor"
#         flash("You need to Login First..")
#         return redirect("/login/auth")
#     return render_template("editor.html")
   

# opens editor
@app.route("/editor/<string:filename>",methods=['GET'])
def editsfilename(filename):
    if 'user' in session:
        userId=session['user']
        if filename=="new":
            url=""
            details=""
        else:
            imgEdits=Images.query.filter_by(userId=userId,image=filename).order_by(Images.date.desc()).first()
            if imgEdits is None:
                return abort(404)
            url="http://127.0.0.1:4000/static/savedImg/"+str(userId)+"/"+imgEdits.image
            details=imgEdits.details
        return render_template("editor.html",url=url,filename=filename,details=details)
    else:
        session["redirect_to"]="/editor/"+filename
        flash("You need to Login First..")
        return redirect("/login/auth")
    return render_template("editor.html")
     
 
# saves edited img (api)
@app.route("/save",methods=['POST'])
def saveImg():
    if "user" in session:
        
        user=Users.query.filter_by(id=session['user']).first()
        try:  
            for k,v in directories.items():
                dir_name=os.path.abspath("../"+directories['savedImg']+"/"+str(user.id))
                if not os.path.exists(dir_name):
                    try:
                        os.mkdir(dir_name)
                    except:
                        os.makedirs(dir_name)
        except:
            pass
        app.config['UPLOAD_FOLDER']= os.path.abspath("../"+directories['savedImg']+"/"+str(user.id))
        
        image= request.files.get('image')
        filename= request.form.get('filename')
        details=request.form.get("details")
        
        # print(filename,image)
        uploads=Images.query.filter_by(userId=session['user']).all()
        if len(uploads)>=9:
            return  make_response(jsonify({'error': "You cannot save the image because you have reached the limit of your free cloud storage."}), 400)
        userId=session['user']
        imgEdits=Images.query.filter_by(image=filename,userId=userId).first()
        if imgEdits:
            
            imgEdits.details=details
            image = Image.open(image.stream)
            imageName=filename 
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imageName) )) 
            imgEdits.image=secure_filename(imageName)
            db.session.commit()
            return  make_response(jsonify({'message': 'Changes has been saved successfully.',"status":"ok"}), 201)
            
        
        if image:
            id = uuid.uuid4().hex
            image = Image.open(image.stream)
            imageName="image_"+str(id)+".png" 
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imageName) ))   
            image=secure_filename(imageName) 
            # try:
            cred=Images(id=id,userId=user.id, image=secure_filename(image),details=details,date=datetime.now())
            db.session.add(cred)
            db.session.commit()
            return  make_response(jsonify({'message': 'Image has been saved successfully.',"status":"ok","filename":secure_filename(imageName)}), 201)

            # except:
            #     return  make_response(jsonify({'error': 'Failed to save Image.'}), 400)
    return  make_response(jsonify({'error': 'Failed to save Image.'}), 400)
    
    # return  make_response(jsonify({'error': 'Required fields are missing'}), 400)

# generates Image
@app.route("/image-generate",methods=['POST'])
def imgGen():
        # set up API credentials and base URL
    access_key =params["unsplash_access_key"]
    secret_key = params["unsplash_secret_key"]
    base_url = "https://api.unsplash.com"
    urls=[]

    # define search query
    query =request.form.get('query')
    paramsBody = {
    "query": query,
    "per_page": 32,
    "orientation": "landscape",
      "w": 650,
        "h": 450
}
    # make API request to search for photos
    response = requests.get(f"{base_url}/search/photos", params= paramsBody, headers={"Authorization": f"Client-ID {access_key}"})
    data = json.loads(response.text)
    # print(data)
    # loop through photos and get their URLs
    for photo in data["results"]:
        urls.append(photo["urls"]["regular"])
    
    if len(urls)<5:
        return  make_response(jsonify({'error': "Images can't get generated."}), 400)
        
        
    return  make_response(jsonify({'message': 'Images has been generated.',"images":urls}), 200)
 


# shows edited images
@app.route("/images",methods=['GET','POST',"DELETE"])   
def images():
    if 'user' in session:
        userId=session['user']
        if request.method=="POST":
            data = request.get_json()
            # Check if the required fields are present in the request body
            required_fields = ['id','operation']
            if not all(field in data for field in required_fields):
                return  make_response(jsonify({'error': 'Some error occured'}), 400)
           
            id=data["id"]
            if data["operation"]=="delete":
                try:
                    imgEdit=Images.query.filter_by(userId=userId,id=id).order_by(Images.date.desc()).first()
                    path=os.path.abspath("../"+directories['savedImg']+"/"+str(userId)+"/"+imgEdit.image)
                    os.remove(path,dir_fd=None)
                    db.session.delete(imgEdit)
                    db.session.commit()
                    return  make_response(jsonify({'message': 'Image has been deleted successfully.'}),  200)
                except:
                    return  make_response(jsonify({'error': 'Failed to delete Image.'}), 400)
                    
            
       
        imgEdits=Images.query.filter_by(userId=userId).order_by(Images.date.desc()).all()
        path="/savedImg/"+str(userId)+"/"
        return render_template("images.html",imgEdits=imgEdits,path=path)
    else:
        session["redirect_to"]="/"
        return redirect("/login/auth")
    
  



  
  #chats

# chats
@app.route("/chats" ,methods=["GET","POST"])
def chats():
    if  'user' in session:
        data=Users.query.filter_by(id=session['user']).first()
        if request.method=="POST":
            msg=request.form.get("msg")
            receiver= "0"
            sender=data.id
            userId=data.id
            cred=Chats(sender=sender,msg=msg,receiver=receiver,userId=userId,date=datetime.utcnow())
            db.session.add(cred)
            db.session.commit()
        
        chats=Chats.query.filter_by(userId=data.id).all()
        Arr=[]
        for key in chats:
            Arr.append(key.toDict())
        
        return {
            "code":200,
            "data":Arr
        }
        
    return {
            "code":400,
            "data":None
        }

#  **************************************ERRORS**********************************************

# handles error 400
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html',error=error), 404

# handles error 400
@app.route("/error")
def error():
    error=400
    return render_template('page_not_found.html',error=error), 404

#  ***************************************UNUSED*******************************************
# otp generator 
@app.route("/generate/otp/for=<id>",methods=['GET','POST'])   
def otpGen(id):
    if 'user' in session:
        user=Users.query.filter_by(id=session['user']).first()
        digits=[i for i in range(0,10)]
        otp=""
        for i in range(6):
            index=math.floor(random.random()*10)
            otp+=str(digits[index])
        title="You recieved new otp from "+params['mainTitle']
        msg= "Your otp is <b><u>%s</u></b> please confirm your order." %(otp)
        to=user.email
        response= sendMail(title,msg,to)
        print(response)
        return {"otp": otp,
           "response":response["status-code"]
        }
    
# send email for otp    
@app.route("/send/title=<string:title>&msg=<string:msg>&to=<string:to>",methods=['GET','POST'])
def sendMail(title,msg,to):
    app.config.update(
    MAIL_SERVER ='smtp.gmail.com',
    MAIL_PORT ='587',
    MAIL_USE_TLS= True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
    )
    mail=Mail(app)
    try:
        mail.send_message(
        title,
        sender=params['gmail_user'],
        recipients=[to],
        body=msg,
        html=msg)
        return {
            "status":"success",
            "status-code":200,
            "msg":"sent successfully"
        }
    except:
        return {
            "status":"failed",
            "status-code":400,
            "msg":"not sent! give another shot..."
        }



@app.context_processor
def inject_user():
    user=None
    if 'user' in session:
        user=Users.query.filter_by(id=session['user']).first()
    return dict(params=params,user=user)  
