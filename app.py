from flask import Flask, render_template,request
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy(app)


# database configuration
# location of db
BASE_DIR = os.path.abspath(os.path.dirname(__file__))+ "/"
# initialize db
# configure flask to know where the db is located
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR + "blogpointdb.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(BASE_DIR)
# classes

# user table
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(100), index=True, unique=True)
    blogs = db.relationship('Blog', backref='author',lazy='dynamic')

    def __repr__(self):
        return self.username


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))



import models
# localhost:3000/
@app.route('/')
def index():
    return render_template('index.html')

# #############Authentication ######################

# localhost:3000/login
@app.route('/login')
def login():
    return render_template('login.html')


# localhost:3000/signup
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username=username,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('login.html')
    return render_template('signup.html', title="Signup page")


@app.route('/account/<int:user_id>')
def account(user_id):
    return render_template('account.html')

################post routes#################
@app.route('/posts/add')
def posts_add():
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
