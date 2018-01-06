from flask import Flask, request, redirect, render_template, session, flash
from models import User, Blog
from app import app, db


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Taken from get-it-done, may need modification."""
    name_error = ''
    pass_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if len(username) < 1:
            name_error = 'Please enter a username.'
            return render_template('login.html', name_error=name_error)
        if not user:
            name_error = 'That username does not exist'
            return render_template('login.html', name_error=name_error)
        if user:
            if user.password != password:
                pass_error = "Password Incorrect.  Please Re-enter Password"
                return render_template('login.html', pass_error=pass_error, username=username)
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        return render_template('login.html', name_error=name_error, pass_error=pass_error)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''Taken from get-it-done, may need modification, check indentation levels.'''
    name_error = ''
    pass_error = ''
    verify_error = ''
    user_taken = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3:
            name_error = "Username must be at least 3 characters long"
        if len(password) < 3:
            pass_error = "Password must be at least 3 characters long"
        if verify != password:
            verify_error = "Passwords do not match"

        existing_user = User.query.filter_by(username=username).first()
        if not name_error and not pass_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                user_taken = "That username is already taken."
                return render_template('signup.html', user_taken=user_taken)
        else:
            return render_template('signup.html', name_error=name_error, pass_error=pass_error, verify_error=verify_error)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_owner = User.query.filter_by(username=session['username']).first()
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
    user_exists = request.args.get('user')
    if id_exists:
        individual_entry = Blog.query.get(id_exists)
        return render_template('/singlepost.html', individual_entry=individual_entry)
    if user_exists:
        user_entry = User.query.filter_by(username=user_exists).first()
        owner_blogs = Blog.query.filter_by(owner=user_entry).all()
        return render_template('/user_post.html', owner_blogs=owner_blogs, owner=user_entry)
    else:
        entries = Blog.query.all()
        return render_template('blog.html', entries=entries)


@app.route('/', methods=['POST', 'GET'])
def index():
    """Returns a List of usernames that when clicked, displays a page of the corresponding
    blog posts of said user."""
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == "__main__":
    app.run()
