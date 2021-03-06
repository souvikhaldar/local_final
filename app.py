from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
#from data import Articles
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,IntegerField
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)
#Articles=Articles()

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='245492'
app.config['MYSQL_DB']='hisabkitab'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql=MySQL(app)



@app.route('/')
def index():
    return render_template("home.html")

#check if logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, please log in','danger')
            return redirect(url_for('login'))
    return wrap



@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/insights',methods=['POST','GET'])
def insights():
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select sum(body) as sum from articles where author=%s",(session['username'],))
    insights=cur.fetchall()
    a=list(insights[0].values())
    result=cur.execute("select max(body) as maxi from articles where author=%s",(session['username'],))
    maxi=cur.fetchall()
    b=list(maxi[0].values())

    #identity=session['username']    

    result=cur.execute("select min(body) as mini from articles where author=%s",(session['username'],))
    mini=cur.fetchall()
    c=list(mini[0].values())
    
    
    #if insights>0:
    return render_template('insights.html',insights=a[0],maxi=b[0],mini=c[0])
    #else:
     #   msg="No expense found"
      #  return render_template('insights.html',msg=msg)
    #close connection
    cur.close()




    
'''
#articles
@app.route('/expenses')
@is_logged_in
def articles():

    
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles")
    articles=cur.fetchall()
    if result>0:
        return render_template('expenses.html',articles=articles)
    else:
        msg="No expenditure found"
        return render_template('expenses.html',msg=msg)
    #close connection
    cur.close()

@app.route('/expenses/<string:id>/')
def article(id):
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles where id= %s",[id])
    
    article=cur.fetchone()
    return render_template('expenses.html',article=article)
    
'''    
class RegisterForm(Form):
	name=StringField('Name',[validators.Length(min=1,max=30)])
	username=StringField('Username',[validators.Length(min=5,max=100)])
	email=StringField('Email',[validators.Length(min=5,max=50)])
	password=PasswordField('Password',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
		])
	confirm=PasswordField('Confirm Password')
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))
        cur=mysql.connection.cursor()
        cur.execute("insert into users(name,email,username,password) values (%s, %s, %s, %s)",(name,email,username,password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered','success')
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username= request.form['username']
        password_candidate=request.form['password']
        cur=mysql.connection.cursor()
        #get user by username
        result=cur.execute("select * from users where username=%s",[username])
        if result>0:
            data=cur.fetchone()
            password=data['password']
            #compare the passwords
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in']=True
                session['username']=username
                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error='Password wrong'
                return render_template('login.html',error=error)
            #close connection
            cur.close()
        else:
            error='Username not found'
            return render_template('login.html',error=error)
            
    return render_template('login.html')



#log out
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out",'success')
    return redirect(url_for('login'))
#dashboard
@app.route('/dashboard',methods=['GET','POST'])
@is_logged_in
def dashboard():
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles")
    articles=cur.fetchall()
    if result>0:
        return render_template('dashboard.html',articles=articles)
    else:
        msg="No expenditures found"
        return render_template('dashboard.html',msg=msg)
    #close connection
    cur.close()
#article form
class ArticleForm(Form):
	expense=StringField('Expense',[validators.Length(min=1,max=300)])
	amount=IntegerField('Amount', [validators.NumberRange(min=0, max=10000000)])

	

#add article
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        expense=form.expense.data
        amount=form.amount.data

        #create cursor
        cur=mysql.connection.cursor()

        cur.execute("insert into articles(title,body,author) values(%s,%s,%s)",(expense,amount,session['username']))
        #commit
        mysql.connection.commit()
        #close connection
        cur.close()
        flash('expenditure listed','success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form)
#edit article
'''
@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    cur=mysql.connection.cursor()
    #get article by id
    result=cur.execute("select * from articles where id=%s",[id])
    article=cur.fetchone()
    #get form
    form=ArticleForm(request.form)
    #populate article form fields
    form.expense.data=article['title']
    form.amount.data=article['body']

    
    if request.method=='POST' and form.validate():
        expense=request.form['expense']
        amount=request.form['amount']

        #create cursor
        cur=mysql.connection.cursor()
        cur.execute("update articles set title=%s,body=%d where id=%s",(expense,amount,id))
           #commit
        mysql.connection.commit()
        #close connection
        cur.close()
        flash('Your expenditure has been updated','success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html',form=form) '''

#delete article
@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
           cur=mysql.connection.cursor()
           cur.execute("delete from articles where id=%s",[id])
           mysql.connection.commit()
           cur.close()
           
           flash('The expenditure has been deleted','success')
           return redirect(url_for('dashboard'))
           
if __name__=='__main__':
    app.secret_key='12345'
    app.run(debug=True)
