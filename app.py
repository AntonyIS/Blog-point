from flask import Flask, render_template,request, flash,redirect, url_for
# import password harsher
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager, login_user, logout_user




app = Flask(__name__)
db = SQLAlchemy(app)


# database configuration
# location of db
BASE_DIR = os.path.abspath(os.path.dirname(__file__))+ "/"
# initialize db
# configure flask to know where the db is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR + "blogpointdb.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secret key security purposes"


login = LoginManager(app)
"""
The Flask-Login extension works with the application's user model, and expects certain properties and methods to be 
implemented in it. This approach is nice, because as long as these required items are added to the model, Flask-Login 
does not have any other requirements, so for example, it can work with user models that are based on any database system.
"""


# UserMixin:
# Flask-Login provides a mixin class called UserMixin that includes generic implementations
# that are appropriate for most user model classes.

# classes
# user table
class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    bio = db.Column(db.String(300), index=True, unique=True)
    password = db.Column(db.String(100), index=True, unique=True)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    blogs = db.relationship('Blog', backref='author',lazy='dynamic')

    def __repr__(self):
        return self.username



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(100))
    blog_image = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    blogger = db.Column(db.String(100))

# Flask-Login keeps track of the logged in user by storing its unique identifier in Flask's user session, a storage space '
# 'assigned to each user who connects to the application. Each time the logged-in user navigates to a new page, Flask-Login'
#  retrieves the ID of the user from the session, and then loads that user into memory.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# localhost:3000/
@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('index.html', title="BLogPoint | Home", blogs=blogs)

# #############Authentication ######################


# localhost:3000/signup
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # check if user exists in the datebase
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash("User exists, login ")
            return redirect(url_for('login'))
        password_hash = generate_password_hash(password)
        user = User(username=username,email=email, password=password_hash)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("signup successful")
        # if signup is successful, the message above will be flashed on the login page
        return render_template('login.html')
    return render_template('signup.html', title="Signup page")

# localhost:3000/login

@app.route('/login', methods=['POST','GET'])
def login():
    # collect form data
    if request.method == 'POST':
        # check if empty
        if request.form['email'] == None or request.form['password'] == None:
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(email= request.form['email']).first()
            # check if password match
            if user is None or not user.check_password(request.form['password']):
                flash('Invalid username or password', 'alert alert-danger')
                return redirect(url_for('login'))
            login_user(user)
            flash('Login successful', 'alert alert-success')
            return redirect(url_for('index'))
    return render_template('login.html', title="Antony Injila | Login")


# localhost:3000/logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>',methods=['GET','POST'])
def profile(user_id):
    user = User.query.get(user_id)
    blogs = user.blogs
   
    if request.form == 'POST' or request.files:
        username = request.form['username']
        bio = request.form['bio']
        image_old = request.form['old_image']
        # process image upload
        # new image upload
        file_new = request.files['new_image']
        # if user is update data together with image
        if file_new:
            filename = secure_filename(file_new.filename)
            # save image in the images folder
            profile_image = "static/images/{}".format(filename)
            file_new.save(BASE_DIR + "static/images/" + filename)
            user.username = username
            user.bio = bio
            user.profile_pic = profile_image
            db.session.commit()
            return redirect(url_for('profile', user_id=user_id))
        # if user is update data without image
        profile_image = image_old
        user.username = username
        user.bio = bio
        user.profile_pic = profile_image
        db.session.commit()

        return redirect(url_for('profile',user_id=user_id))
    return render_template('account.html', user=user)


@app.route('/blogger/<username>')
def blogger(username):
    user = User.query.filter_by(username=username).first()
    return render_template('blogger.html', user=user)

################post routes#################
@app.route('/posts/add', methods=['GET','POST'])
def posts_add():
    
    if request.method == 'POST':
        bloggerID= request.form['userID']
        title= request.form['title']
        body= request.form['description']
        
        # get user object
        user =User.query.get(bloggerID)
        # if images was uploaded
        file_new = request.files['blog_image']
        if file_new:
            filename = secure_filename(file_new.filename)
            # save image in the images folder
            blog_image = "static/images/blogs/{}".format(filename)
            file_new.save(BASE_DIR + "static/images/blogs/" + filename)

            new_blog = Blog(title=title,body=body,blog_image= blog_image, blogger=user.username)
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for("index"))
        # if user does not add an image, assign a default image
        blog_image = "static/images/blogs/defaultimg.jpg"  
        new_blog = Blog(title=title,body=body,blog_image= blog_image)
        db.session.add(new_blog)   
        db.session.commit()
        return redirect(url_for("index"))
    return render_template('posts.html')

@app.route('/posts/detail/<int:post_id>')
def posts_details(post_id):
    return render_template('post_detail.html')


@app.route('/posts/update/<int:post_id>')
def posts_update(post_id):
    return render_template('post_update.html')

@app.route('/posts/delete/<int:post_id>')
def posts_delete(post_id):
    return render_template('index.html')













# Error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error),404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'),500


if __name__ == '__main__':
    app.run(port=3000, debug=True)
