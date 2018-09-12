#!/usr/bin/python3

from flask import Flask, url_for, render_template, request, flash, redirect
from flask_uploads import UploadSet, configure_uploads, IMAGES
from slugify import slugify
from flask_sqlalchemy import *
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, logout_user, login_user, current_user, login_required, login_manager
from datetime import datetime
from forms import LoginForm, RegistrationForm, AddEditPost
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_scss import Scss
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters
from werkzeug.utils import secure_filename
from wtforms_sqlalchemy.fields import QuerySelectField
import os, re

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'postgresql://localhost/blogdatabase'


UPLOAD_FOLDER = project_dir + "/static/media/images/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)
Scss(app, static_dir='static/styles', asset_dir='assets')


app.config['SECRET_KEY'] = 'sjshlaiyeiruhkjgavksnlkvnslvsnlvsnlvnsdh536574988tufaa7v02j4ueyv7iu2' #TEMPORARY KEY, CHANGE IN PRODUCTION
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

login.login_view = 'login'


#DATABASE MODELS

#Posts Table
class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    date_posted = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    title = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, default = id, nullable=False)
    category = db.Column(db.String(80))
    draft = db.Column(db.Boolean(), default = True)
    body = db.Column(db.Text())
    header_image = db.Column(db.String)
    header_image_path = db.Column(db.String)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

# Automatic Slug generation (using slugify) (PART OF POSTS MODEL)
    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if not target.slug:
            target.slug = slugify(value)

event.listen(Post.title, 'set', Post.generate_slug, retval=False)

#Users Table
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#User Loader
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#Home Page Route
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Image': Image}

#Makes Titles Titlecase
def title_case(s):
    word_list = re.split(' ', s)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    articles = ['a', 'an', 'of', 'the', 'is', 'but', 'or', 'nor', 'for']
    for word in word_list[1:]:
        final.append(word if word in articles else word.capitalize())
    return " ".join(final)

#Homepage route
@app.route('/')
@app.route('/index')
def index():
    title = 'Antoni Devlin | Blog'
    posts = Post.query.filter_by(draft=False).order_by(Post.date_posted.desc()) #Only shows published posts (Those without the 'draft' flag set).
    return render_template('index.html', posts=posts, title=title)

#Admin Dashboard route
@app.route('/admin')
@app.route('/dashboard')
@login_required
def admin():
    posts = Post.query.order_by(Post.date_posted.desc())
    return render_template('admin.html', posts=posts)

def category_choice():
    return Category.query


#New Post Route
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddEditPost()
    post = Post()
    if form.validate_on_submit():
        if form.header_image.data !='' :
            filename = secure_filename(form.header_image.data.filename)
            fullpath = UPLOAD_FOLDER + filename
            form.header_image.data.save(fullpath)

            post = Post(title = form.title.data, category = form.category.data, draft = form.draft.data, body = form.body.data, header_image = filename, header_image_path = fullpath)

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            post = Post(title = form.title.data, category = form.category.data, draft = form.draft.data, body = form.body.data)

            db.session.add(post)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form, post = post)

# Edit Post Route
@app.route('/edit/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = AddEditPost(obj=post)
    header_image = post.header_image
    if form.validate_on_submit():
        if form.header_image.data !='' :
            filename = secure_filename(form.header_image.data.filename)
            fullpath = UPLOAD_FOLDER + filename
            form.header_image.data.save(fullpath)

            post.title = form.title.data
            post.category = form.category.data
            post.draft = form.draft.data
            post.body = form.body.data
            post.header_image = filename
            post.header_image_path = fullpath
            db.session.commit()
            return redirect(url_for('index'))
        else:
            post.title = form.title.data
            post.category = form.category.data
            post.draft = form.draft.data
            post.body = form.body.data
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add.html', form=form, title='Edit Post', post = post)

@app.route('/images')
def images():
    images = Image.query.order_by(Image.date_posted.desc())
    return render_template('images.html', images=images)

#Delete Post Route
@app.route('/delete/<string:slug>')
@login_required
def delete_post(slug):
    Post.query.filter_by(slug=slug).delete()
    db.session.commit()
    return redirect(url_for('index'))

# display post by slug
@app.route('/post/<string:slug>')
def byslug(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template("post.html", post=post, slug=slug)



#Display category page
@app.route('/<string:category>')
def bycategory(category):
    posts = Post.query.filter_by(category=category)
    return render_template("categorylist.html", posts=posts, category=category)

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

#Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#Contact Page Route
@app.route('/contact')
def contact():
    title = 'Contact'
    return render_template('contact.html', title=title)

#About Page Route
@app.route('/about')
def about():
    title = 'About'
    return render_template('about.html', title=title)

# ERROR HANDLING

# Error 404
@app.errorhandler(404)
def page_not_found(e):
    title = 'Not Found'
    return render_template('404.html', title=title), 404
