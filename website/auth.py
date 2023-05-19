from flask import Blueprint, jsonify, redirect,render_template,request,flash,Response, url_for, session
import json
from . import conn
from werkzeug.security import generate_password_hash, check_password_hash
# from bson.objectid import ObjectId
from flask_session import Session
auth = Blueprint('auth',__name__)
db = conn.connection()

@auth.route('/login',methods=['GET','POST'])
def login():
    print("In the login afunction ")
    # session["name"] = None
    if request.method == 'POST':

        email = request.form.get('email')

        password = request.form.get('password')

        account = request.form.get('account')
    
        if account == 'admin':
            user = db.Admin.find_one({"email":email})
        else:
            user = db.customers.find_one({"email":email})

        if user ==[]:
            flash('No Account is Registered with this Email ',category='error')
        elif (not check_password_hash(user["password"],password)):
            flash('Incorrect Password',category='error')
        else:
            print(user["email"])
            session["name"] = user["email"]
            session["account"]= account
            session["cart"]=[]
            session["qty"]=[]
            print("session name is :")
            print(session["name"], session["account"])
            flash('Login Successfull!!',category='success')
            return redirect(url_for('views.home'))

    return render_template("/login.html",text="Testing a variable from backend")
    # return redirect(url_for('views.home'))





@auth.route("/logout")
def logout():
    print("inside logout")
    session["name"]=None
    session["account"]=None
    session["cart"]=None
    session["qty"]=None
    print("Session name is :",session["name"])
    return redirect(url_for('views.home'))

@auth.route('/sign-up',methods=['GET','POST'])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        phno      = request.form.get('phone')
        country      = request.form.get('country')
        street1      = request.form.get('street1')
        street2      = request.form.get('street2')
        city      = request.form.get('city')
        state      = request.form.get('state')
        zip      = request.form.get('zip')
        cardtype      = request.form.get('cardtype')
        cardno      = request.form.get('cardno')
        expdate      = request.form.get('expdate')
        name      = request.form.get('name')
        if len(email)<4:
            flash('Email must be greater than 3 characters',category='error')
        elif len(firstName)<2:
            flash('firstName must be greater than 2 characters',category='error')
        elif password1!= password2:
            flash('passwords dont match',category='error')
        elif len(password1) <3:
            flash('password must be atleast 3 chasracters',category='error')
        else:
            try:
                print("Inside Try Block ")
                input_data = {
                    "firstName":firstName,
                    "email":email,
                    "password": generate_password_hash(password1,method='sha256'),
                    "phno":phno,
                    "address":{
                        "country":country,
                        "street1":street1,
                        "street2":street2,
                        "city":city,
                        "state":state,
                        "zip":zip
                        },
                    "shipping_address":{
                        "country":country,
                        "street1":street1,
                        "street2":street2,
                        "city":city,
                        "state":state,
                        "zip":zip
                        },    
                    "payment_details":{
                        "card_type":cardtype,
                        "card_number":cardno,
                        "exp_date":expdate,
                        "Name":name
                        }
                    }
                
                db.customers.insert_one(input_data)
                flash('Account created!!',category='success')
                return redirect(url_for('views.home'))
            except Exception as ex:
                return Response(
                response=  json.dumps({"Message":"Error Occurred while Inserting New Record!!"}),
                status=500,
                mimetype="application/json"
                )
    return render_template("sign-up.html")