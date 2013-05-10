from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import escape
from flask_mail import Mail, Message
import sqlite3
app = Flask(__name__)
mail = Mail(app)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'gmailuser@gmail.com',
    MAIL_PASSWORD = 'gmailpass',
    DEFAULT_MAIL_SENDER = 'gmailuser@gmail.com'
    )

app.secret_key = '!@#$%^WR@FDFEQW!#@$#TET%$Y^$UT#WRQW!@#2412413FT$T#%YY^$U%'

itemname=['A4 lecture pad','7-colour sticky note with pen','A5 ring book','A5 note book with zip bag','2B pencil','Stainless steel tumbler','A4 clear holder','A4 vanguard file','Name card holder','Umbrella','School badge (Junior High)','School badge (Senior High)','Dunman dolls (pair)']
itemprice=[2.60,4.20,4.80,4.60,0.90,12.90,4.40,1.00,10.90,9.00,1.30,1.80,45.00]

def valid_login(username,password):
    with sqlite3.connect("users.db") as connection:
        c = connection.cursor()
        c.execute("SELECT * FROM USERS")
        total = c.fetchall()
    numpassword=hash(password)
    for s in total:
        if s[0]==username and s[1]==numpassword:
            return True
    return False

def confirmused(username):
    with sqlite3.connect("users.db") as connection:
        c = connection.cursor()
        c.execute("SELECT * FROM USERS")
        total = c.fetchall()
    for s in total:
        if s[0]==username:
            return True
    return False

def valid_signup(username, password, repassword, email):
    if (password!=repassword) or (len(username)>15) or (len(password)>12) or (len(password)<4) or (confirmused(username)) or (not '@' in email):
        return False
    for s in username:
        if not(s.isalpha() or s.isdigit()):
            return False
    for s in password:
        if not(s.isalpha() or s.isdigit()):
            return False
    return True

def save(username, password, email, address):
    orderinformation='0X0X0X0X0X0X0X0X0X0X0X0X0'
    numpassword=hash(password)
    with sqlite3.connect("users.db") as connection:
        c = connection.cursor()
        c.execute("CREATE TABLE if not exists users(username TEXT, password INT, email TEXT, address TEXT, orderinformation TEXT)")
        c.execute("INSERT INTO users VALUES(?,?,?,?,?)", (username, numpassword, email, address, orderinformation))

@app.route('/confirm/', methods=['POST', 'GET'])
def confirm():
    if 'username' in session:
        username=escape(session['username'])
        if request.method == 'POST':
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("SELECT email FROM USERS WHERE username='%s'" % username)
                total=c.fetchall()
            orders='0X0X0X0X0X0X0X0X0X0X0X0X0'
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("UPDATE users SET orderinformation = '%s' WHERE username='%s'" % (orders,username))
            try:
                email=str(total[0][0])
                msg = Message("Hello",sender=("noreply@pythonanywhere.com"),recipients=[email])
                msg.body = "Test!"
                mail.send(msg)
            except:
                error = 'Sorry, the confirmation email cannot be sent. :('
                return render_template('confirm.html', error=error)
        else:
            return render_template('confirm.html')
    else:
        return redirect('/')

@app.route('/cart/', methods=['POST', 'GET'])
def cart():
    if 'username' in session:
        username=escape(session['username'])
        if request.method == 'POST':
            cancel=request.form.get('cancel', None)
            if cancel == 'Cancel all orders':
                orders='0X0X0X0X0X0X0X0X0X0X0X0X0'
                with sqlite3.connect("users.db") as connection:
                    c = connection.cursor()
                    c.execute("UPDATE users SET orderinformation = '%s' WHERE username='%s'" % (orders,username))
                return redirect('/')
            else:
                return redirect('/confirm/')
            return redirect('/')
        else:
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("SELECT orderinformation FROM USERS WHERE username='%s'" % username)
                info = c.fetchall()
            if info:
                orderinformation = str(info[0][0])
            else:
                orderinformation = ''
            items=[]
            total=0
            sp=orderinformation.split('X')
            if orderinformation!='':
                for s in sp:
                    if int(s)!=0:
                        i=sp.index(s)
                        try:
                            item=[itemname[i], int(s), itemprice[i]]
                        except:
                            return str(i)+orderinformation
                        total+=item[1]*item[2]
                        items.append(item)
            else:
                items=None
                orderinformation=''
                total=None
            return render_template('cart.html', items=items, total=total)
    else:
        return redirect('/login/')

@app.route('/order/', methods=['POST', 'GET'])
def order():
    if request.method == 'POST':
        if 'username' in session:
            username = escape(session['username'])
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("SELECT orderinformation FROM users where username='%s'" % username)
                t=c.fetchall()
            orderinformation=str(t[0][0])
            sp=orderinformation.split('X')
            orders=''
            for i in range(1,13):
                try:
                    x=int(request.form['item'+str(i)])+int(sp[i-1])
                except:
                    x=0
                orders+=str(x)+'X'
            try:
                orders+=str(int(request.form['item13'])+int(sp[12]))
            except:
                orders+='0'
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("UPDATE users SET orderinformation = '%s' WHERE username='%s'" % (orders,username))
            if orders=='0X0X0X0X0X0X0X0X0X0X0X0X0':
                check = 'Please order something before submitting your order'
            else:
                check = 'Your order has been added to the cart :)'
            items=[]
            for i in range(0,13):
                item=[itemname[i]+'.jpg',itemname[i],'item'+str(i+1),'$'+str(itemprice[i]),0]
                items.append(item)
            return render_template('order.html', check=check, items=items)
        else:
            return redirect('/login/')
    else:
        items=[]
        for i in range(0,13):
            item=[itemname[i]+'.jpg',itemname[i],'item'+str(i+1),'$'+str(itemprice[i]),0]
            items.append(item)
        return render_template('order.html', items=items)

@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        button=request.form['button']
        if button=='Check availability':
            username=request.form['username']
            if (len(username)<3):
                check='Invalid username'
                return render_template('signup.html', username=username, check=check)
            if confirmused(username):
                check='Username already exists'
            else:
                check='Username available'
            return render_template('signup.html', username=username, check=check)
        if button=='Register':
            username=request.form['username']
            password=request.form['password']
            repassword=request.form['repassword']
            email=request.form['email']
            address=request.form['address']
            if valid_signup(username,password,repassword,email):
                save(username, password, email, address)
                return redirect('/login/')
            else:
                flag=False
                for s in username:
                    if not(s.isdigit() or s.isalpha()):
                        flag=True
                if (len(username)>15) or (confirmused(username)) or flag:
                    error='Invalid username'
                    return render_template('signup.html', error=error)
                for s in password:
                    if not(s.isdigit() or s.isalpha()):
                        flag=True
                if (password!=repassword) or (len(password)>12) or (len(password)<4) or flag:
                    error='Invalid password'
                    return render_template('signup.html', username=username, error=error)
                if not ('@' in email):
                    error='Invalid email address'
                    return render_template('signup.html', username-username, password=password, repassword=repassword, error=error)
                return redirect('/signup/')
    return render_template('signup.html')

@app.route('/clear/', methods=['POST', 'GET'])
def clear():
    if request.method == 'POST':
        password=request.form['password']
        if hash(password)==-4463228007734255032:
            with sqlite3.connect("users.db") as connection:
                c = connection.cursor()
                c.execute("DROP TABLE IF EXISTS USERS")
                c.execute("CREATE TABLE users(username TEXT, password INT, email TEXT, address TEXT, orderinformation TEXT)")
            return 'Dear administrator: clear up alr:)'
        else:
            return 'Please do not hack my site :)'
    else:
        return render_template('clear.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        if valid_login(username,password):
            session['username'] = username
            return redirect('/')
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/')
def index(name=None):
    if 'username' in session:
        return render_template('index.html', username=escape(session['username']))
    else:
        return render_template('index.html')

@app.route('/search/', methods=['POST','GET'])
def search():
    if 'username' in session:
        if request.method == 'POST':
            keyword=str(request.form['keyword'])
            names=[]
            emails=[]
            with sqlite3.connect('users.db') as connection:
                c = connection.cursor()
                c.execute('SELECT * FROM USERS')
                total = c.fetchall()
            for s in total:
                if keyword.lower() in str(s[0]).lower():
                    name=[str(s[0])]
                    st='email address: '+str(s[2])
                    info=[st]
                    if str(s[3])=='':
                        st="address for delivery: we still don't know his/her address yet"
                    else:
                        st='address for delivery: '+str(s[3])
                    info.append(st)
                    name.append(info)
                    if str(s[4])=='0X0X0X0X0X0X0X0X0X0X0X0X0':
                        name.append(None)
                    else:
                        sp=str(s[4]).split('X')
                        order=[]
                        for ss in sp:
                            if ss!='':
                                if int(ss)!=0:
                                    x=sp.index(ss)
                                    st=ss+'   '+itemname[x]
                                    order.append(st)
                        name.append(order)
                    names.append(name)
                    emails.append(str(s[2]))
            return render_template('search.html', keyword=keyword, names=names, emails=emails)
        else:
            return render_template('search.html', keyword='', names=[])
    else:
        return redirect('/login/')

if __name__ == '__main__':
    app.run(debug=True)