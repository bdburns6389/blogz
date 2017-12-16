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

@app.before_request  #Are the allowed routes correct?
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Taken from get-it-done, may need modification."""
    print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print(user)
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            return '<h1>Wrong</h1>' #What should this actually return?
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''Taken from get-it-done, may need modification, check indentation levels.'''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']  #Verify needs to be used somewhere. Or does it?

        #TODO Validate Data, using verify request data.

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            #TODO message that says already exists in database
            return '<h1>Duplicate User</h1>'

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #Need to add blog.owner to this route, but is it a hidden value?
    blog_owner = User.query.filter_by(username=session['username']).first()
    #This will need to relate toSESSIONS before it will work.
    # Make sure to use username (similar to email in the get it done video)
    #Will also need to be put in like blog_owner=blog_owner in a .query somewhere.
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
            new_entry = Blog(blog_title, blog_body, blog_owner)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id='+str(new_entry.id))  #Accesses id attribute
        else:
            return render_template('/newpost.html', blog_title=blog_title,
                                   blog_body=blog_body, title_error=title_error,
                                   body_error=body_error)

    else:
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


@app.route('/', methods=['POST', 'GET']) #Should be able to change to match new assignment.
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
