"""Flask Blog :D """

from functools import wraps
from flask import Flask, redirect, url_for, session, flash, render_template, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from werkzeug.contrib.cache import SimpleCache

import re
from datetime import datetime
#from functools import wraps
from config import config
#from cgi import escape

cache = SimpleCache()

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/posts.db'

#app.config['USER'] = 'admin'
#app.config['PASSWORD'] = 'default'
app.config['SECRET_KEY'] = 'C5G94WB6BVRPHTO85RGI2Y6TM6HYY0P'


for key in config:
    app.config[key] = config[key]


def cached(timeout=5 * 60, key='cached/%s'):
    # ~200 req/s => ~600-800 req/s
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

slug_re = re.compile('[a-zA-Z0-9]+')

db = SQLAlchemy(app)
Markdown(app)


def slugify(title):
    _title = title[:99].replace(' ', '-')  # Changed slug length to 100
    return '-'.join(re.findall(slug_re, _title))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged = session.get('logged_in', None)
        if not logged:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    html = db.Column(db.String)
    created = db.Column(db.DateTime)
    tags = db.Column(db.String)  # comma seperated values
    slug = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, rawbody, tags, category):
        self.title = title
        self.html = rawbody  # TODO: markdown support
        self.created = datetime.utcnow()
        self.tags = tags
        self.slug = slugify(title)
        self.category = category  # added category to the Post object

    def __unicode__(self):
        return self.slug


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    slug = db.Column(db.String)

    def __init__(self, title):
        self.title = title
        self.slug = slugify(title)

    def __unicode__(self):
        return self.title


@app.template_filter('friendlytime')
def timesince(dt):
    format = "%A, %B %d, %Y"
    #return dt.isoformat()
    return dt.strftime(format)
    #return default


@app.route('/')
@cached(120)  # from 200 req/s to 800 req/s
def index():
    posts = Post.query.order_by('created DESC').limit(app.config['post_count'])
    # Ordering by created time DESC isstead of reversing
    return render_template('index.html', posts=posts)


@app.route('/archive/')
@cached(120)
def all():
    posts = Post.query.all()
    return render_template('archive.html', posts=posts)


@app.route('/p/<slug>/')
@cached(120)
def detail(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post:
        return render_template('detail.html', post=post)
    else:
        abort(404)


@app.route('/new/', methods=['GET', 'POST'])
@login_required
def newpost():
    if request.method == 'POST':
        try:
            title = request.form['title']
            body = request.form['body']
            tags = request.form['tags']
            category = Category.query.filter_by(title=request.form['category']).first()
            # Added first() so that only one category is added
        except Exception as e:
            flash('There was an error with your input: %s' % e)
            return redirect(url_for('newpost'))
        for thing in request.form.keys():  # verification
            if not request.form[thing]:
                flash('Error: %s incorrect.' % thing)
                return redirect(url_for('newpost'))

        p = Post(title, body, tags, category)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('detail', slug=p.slug))
    else:
        categories = Category.query.all()
        return render_template('new.html', categories=categories)


@app.route('/del/<slug>/')
@login_required
def delete(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.")
    else:
        flash("Couldn't delete.")
    return redirect(url_for('index'))


@app.route('/category/<slug>/')
@cached(120)
def showcat(slug):
    cat = Category.query.filter_by(slug=slug).first()
    posts = Post.query.filter_by(category=cat).all()
    return render_template('category.html', posts=posts)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['user']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('index'))
        flash(error)
    return render_template('login.html', error=error)


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
