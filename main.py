from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
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


@app.route("/blog", methods=['POST', 'GET'])
def index():  
    if request.args.get('id'):
        blog_id = int(request.args.get('id'))
        indiv_blog = Blog.query.get(blog_id)
        new_title = indiv_blog.title
        new_body = indiv_blog.body
        date = indiv_blog.date
        return render_template("indiv_blog.html", page_title="Build A Blog", new_title=new_title, new_body=new_body, date=date)
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, page_title="Build A Blog")        


@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    title_error=''
    entry_error=''
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


#@app.route("/signup")


#@app.route("/login")


#@app.route("/index")


#@app.route("/logout", method="POST")
#def logout():
#    del session['']
#    redirect('/blog')




if __name__ == "__main__":
    app.run()