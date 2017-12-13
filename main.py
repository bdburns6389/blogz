from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'root' #should be a better key for security purposes, but oh well, right?


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #Still commits everything to database, rearrange if statements to make this work correctly.
    title_error = ""
    body_error = ""
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        if len(blog_title) < 1:
            title_error = "Please enter a Title for your Blog."
        if len(blog_body) < 1:
            body_error = "Please enter a Body for your Blog."
        if not title_error and not body_error:
            new_entry = Blog(blog_title, blog_body)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id='+str(new_entry.id))  #Accesses id attribute
        else:
            return render_template('/newpost.html', blog_title=blog_title,
                                   blog_body=blog_body, title_error=title_error,
                                   body_error=body_error)

    return render_template('newpost.html')



@app.route('/blog', methods=['POST', 'GET'])
def blog():
    id_exists = request.args.get('id')
    if id_exists:
        individual_entry = Blog.query.get(id_exists)
        return render_template('/singlepost.html', individual_entry=individual_entry)
    else:
        entries = Blog.query.all()
        return render_template('blog.html', entries=entries)


@app.route('/', methods=['POST', 'GET'])
def index():
    entries = Blog.query.all()
    return render_template('blog.html', entries=entries)

if __name__ == "__main__":
    app.run()
