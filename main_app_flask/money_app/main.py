from flask import Flask, jsonify, redirect,url_for, request, render_template, session, flash
from datetime import timedelta
import requests
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

api_host=os.environ.get("API_HOST")
api_port=os.environ.get("API_PORT")

app= Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=5)

## Email
def send_email(to_address,subject,body):
    # Your Gmail credentials
    username = "test0python0code@gmail.com"
    app_password = "hxpa vqfl ukgp emsg"
    # Recipient email address
    to_address = to_address
    # Create a message
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Connect to Gmail's SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    # Login to your Gmail account
    server.login(username, app_password)
    # Send the email
    server.sendmail(username, to_address, msg.as_string())
    # Quit the server
    server.quit()

# connecting to database api to get user's  money
def get_user_money(username):
    query = f'''
        query{{
        user(username: "{username}"){{
            money
            }}
        }}
        '''
    response = requests.post(f'http://{api_host}:{api_port}/graphql', json={'query': query})
    data = response.json()
    user_money = data['data']['user']
    return user_money

# connecting to database api to get user's  money
def get_user_money_email(username):
    query = f'''
        query{{
        user(username: "{username}"){{
            money
            email
            }}
        }}
        '''
    response = requests.post(f'http://{api_host}:{api_port}/graphql', json={'query': query})
    data = response.json()
    user_money_email = data['data']['user']
    return user_money_email

# connecting to database api to get user's  password
def get_user_password(username):
    query = f'''
    query{{
    user(username: "{username}"){{
        password
        }}
    }}
    '''
    response = requests.post(f'http://{api_host}:{api_port}/graphql', json={'query': query})
    data = response.json()
    user_password = data['data']['user']
    return user_password

# connecting to database api to create user
def create_new_user(username,email,password):
    query = f'''
    mutation {{
        createUser( username: "{username}" email: "{email}" password: "{password}"){{
        user{{
        id
        username
        email
        password
        money
            }}
        }}
    }}
    '''
    response = requests.post(f'http://{api_host}:{api_port}/graphql', json={'query': query})
    return response

# connecting to database api to update user's money  
def update_user_money(username,amount):
    query = f'''
    mutation {{
        updateUser(username:"{username}" money:"{amount}"){{
            user{{
            id
            username
            money
            }}
        }}
    }}
    '''
    response = requests.post(f'http://{api_host}:{api_port}/graphql', json={'query': query})
    return response

### routes ###
@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/account/", methods=['GET'])
def account():
    if "username" in session:
        username = session["username"]
        money = get_user_money(username=username)["money"]
        return render_template("account.html", user_name=username,money=money)
    else: 
        return redirect(url_for("login"))

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method == "POST":
        session.permanent=True
        username = request.form["signup_username"]
        email = request.form["signup_email"]
        password = request.form["signup_password"]
        confirm_password = request.form["signup_confirm_password"]
        if not re.match(r'^.{5,}$', username):
            flash('Username should be at least 5 characters long', 'error')
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            flash('Email is wrong', 'error')
        elif not re.match(r'^.{5,}$',password):
            flash('Password should be at least 5 characters long', 'error')
        elif not confirm_password == password:
            flash('Confirm password miss matchs password', 'error')
        else:
            try:
                x= create_new_user(username=username,email=email,password=password)
                session["username"] = username
                try:
                    mail_subject = "New signup"
                    mail_body = f"Welcome {username} To Money App"
                    send_email(email,mail_subject,mail_body) #can be changed to microservice
                except:
                    pass
                return redirect("/account")
            except:
                flash('Username already used try another one', 'error')
        return redirect("/signup")
    elif request.method == "GET":
        return render_template("signup.html")
    
@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == "POST":
        session.permanent=True
        username = request.form["login_username"]
        password = request.form["login_password"]
        user = get_user_password(username=username)
        if user:
            if user["password"] == password:
                session["username"] = username
                return redirect("/account")
            else:
                flash('Wrong Password', 'error')
                return redirect("/login")
        else:
            flash('Please Enter correct username', 'error')
            return redirect("/login")
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout_user():
    session.pop("username")
    return redirect("/")

@app.route("/send", methods=['POST','GET'])
def send():
    if request.method == "POST":
        send_to = request.form["send_to"]
        amount = request.form["send_amount"]
        
        reciver_user = get_user_money(username=send_to)
        if reciver_user:
            if re.match(r'^[1-9]\d*$',amount):
                amount = int(amount)
                send_user = get_user_money_email(username=session["username"])
                if send_user["money"] >= amount:
                    update_user_money(send_to, reciver_user["money"] + amount)
                    update_user_money(session["username"], send_user["money"] - amount)
                    try:
                        mail_subject = "Money Sent by Money App"
                        mail_body = f"Ammount: {amount} sent to {send_to}"
                        send_email(send_user["email"],mail_subject,mail_body) #can be changed to microservice
                    except:
                        pass
                    flash("Money has been sent",'message')
                else:
                    flash("You don't have enough money",'error')
            else:
                flash("Entered amount to send must be positive and not decimal",'error')
        else:
            flash("Reciver username doesn't exist", 'error')
        return render_template("send.html")
    elif request.method == "GET":
        if "username" in session:
            return render_template("send.html")
        else:
            return redirect("/login")

if __name__ == "__main__":
    app.run(port=5000,debug=True)