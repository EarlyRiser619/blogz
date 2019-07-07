from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:coding@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog", methods=['POST', 'GET'])
def index():
    title_error=''
    entry_error=''
    if request.method == "POST":
        blog_title = request.form['title']
        blog_entry = request.form['body']
        new_blog = Blog(blog_title, blog_entry)
        if (not blog_title):
            title_error = "Field must be filled in" 
        if (not blog_entry):
            entry_error= "Field must be filled in"
        if title_error or entry_error:
            return render_template("newpost.html", title_error=title_error, entry_error=entry_error, page_title="New Blog Entry")
        db.session.add(new_blog)
        db.session.commit()
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, page_title="Build A Blog")

    blogs = Blog.query.all()
    return render_template("blog.html", page_title="Build A Blog", blogs=blogs)


@app.route("/blog", methods=['GET'])
def indiv_post():
    blog_id = request.args.get(blog.id)
    indiv_blog = Blog.query.get(blog_id)
    
    return render_template("indiv.html", page_title="Blog Post", indiv_blog=indiv_blog)


@app.route("/newpost", methods=['GET'])
def new_post():
    #new_title = request.form['title']
    #new_body = request.form['body']

    return render_template("newpost.html", page_title="New Blog Entry")



if __name__ == "__main__":
    app.run()