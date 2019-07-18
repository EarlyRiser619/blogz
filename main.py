from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '@b(D#F&hi'',>?renee'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes=['login', 'sign_up', 'bloggies', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/blog", methods=['POST', 'GET'])
def bloggies():  
    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        indiv_blog = Blog.query.get(blog_id)
        #new_title = indiv_blog.title
        #new_body = indiv_blog.body
        #date = indiv_blog.date
        #author = indiv_blog.owner.username
        return render_template("indiv_blog.html", page_title="Build A Blog", indiv_blog=indiv_blog)
    if request.args.get('user'):
        user_id = int(request.args.get('user'))
        author = User.query.get(user_id)
        blogs = author.blogs
        return render_template("singleUser.html", page_title="{{author.username}}'s Blog", author=author, blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, page_title="Build A Blog")        


@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    title_error=''
    entry_error=''
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == "POST":
        blog_title = request.form['title']
        blog_entry = request.form['body']
        if (not blog_title):
            title_error = "Field must be filled in" 
        if (not blog_entry):
            entry_error= "Field must be filled in"
        if title_error or entry_error:
            return render_template("newpost.html", title_error=title_error, entry_error=entry_error, page_title="New Blog Entry")
        new_blog = Blog(blog_title, blog_entry, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = new_blog.id
        return redirect("/blog?id=" + str(blog_id))
    return render_template("newpost.html", page_title="New Blog Entry")


@app.route("/signup", methods=['POST', 'GET'])
def sign_up():
    user_error = False
    pass_error = False
    ver_error = False
    if request.method == 'POST':
        username = request.form['username']
        if (not username) or (username.strip() == '') or (len(username) < 3) or len(username) > 20 or (' ' in username):
            flash('Please re-type your name. It must contain between 3 and 20 characters and have no spaces', 'error')
            user_error = True
        password = request.form['password']
        if (not password) or (password.strip() == '') or (len(password)< 3) or (len(password) > 20) or (' ' in password):
            flash('Please type in a valid password. It must contain between 3 and 20 characters and have no spaces', 'error')
            pass_error = True
        verify = request.form['verify']
        if (not password) or (password.strip() == '') or(verify != password):
            flash('Passwords do not match', 'error')
            ver_error = True
        if user_error or pass_error or ver_error:
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('This username already exists', 'error')

    return render_template('signup.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if user and user.password != password:
            flash('User password incorrect', 'error')
            return redirect('/login')
        if not user:
            flash('User name does not exist', 'error')
    return render_template('login.html')



@app.route("/")
def index():
    authors = User.query.all()
    return render_template('index.html', authors=authors, page_title="Author List")


@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')




if __name__ == "__main__":
    app.run()