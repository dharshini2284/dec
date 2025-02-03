from flask import Flask,render_template,request,session,flash,redirect,url_for
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3;

app=Flask(__name__)
app.secret_key="your_secret_key"

def init_db():
    with sqlite3.connect('data.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT NOT NULL UNIQUE,password TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,name TEXT NOT NULL)''')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        with sqlite3.connect('data.db') as conn:
            try:
                conn.execute('INSERT INTO users (username,password) VALUES (?,?)',(username,generate_password_hash(password)))
                flash("Account created successfully!")
                return redirect(url_for('signin'))
            except sqlite3.IntegrityError:
                flash("Username already exists!")
    return render_template('signup.html')
@app.route('/signin',methods=['POST','GET'])
def signin():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        with sqlite3.connect('data.db') as conn:
            user=conn.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
            if user and check_password_hash(user[2],password):
                session['username']=username
                flash("Signin successfull!")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password!")
    return render_template('signin.html')
@app.route('/logout')
def logout():
    session.pop('username',None)
    flash("Logged out successfully!")
    return redirect(url_for('signin'))
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('signin'))
    with sqlite3.connect('data.db') as conn:
        items=conn.execute('SELECT * FROM items').fetchall()
    return render_template('home.html',items=items)

@app.route('/add',methods=['POST','GET'])
def add():
    if 'username' not in session:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        name=request.form['name']
        with sqlite3.connect('data.db') as conn:
            conn.execute('INSERT INTO items (name) VALUES (?)',(name,))
            flash("Item added successfully!")
            return redirect(url_for('home'))
    return render_template('add.html')
@app.route('/update/<int:item_id>',methods=['POST','GET'])
def update(item_id):
    if 'username' not in session:
        return redirect(url_for('signin'))
    with sqlite3.connect('data.db') as conn:
        if request.method == 'POST':
            name=request.form['name']
            conn.execute('UPDATE items SET name = ? WHERE id=?',(name,item_id))
            flash("Item updated successfully!")
            return redirect(url_for('home'))
        item=conn.execute('SELECT * FROM items WHERE id=?',(item_id,)).fetchone()
    return render_template('update.html',item=item)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    if 'username' not in session:
        return redirect(url_for('signin'))
    with sqlite3.connect('data.db') as conn:
        conn.execute('DELETE FROM items WHERE id=?',(item_id,))
        flash("Item deleted successfully!")
        return redirect(url_for('home'))
init_db()
@app.route('/')
def index():
    return render_template('signin.html')  
if(__name__)=="__main__":
    app.run(debug=True,port=8080)