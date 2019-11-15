import os
from datetime import datetime

from flask import Flask, request, abort, render_template,  redirect,  url_for, flash
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

from forms import ContactForm, LoginForm


app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')


manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app,  db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin'))

        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html', name='Jerry')
    # return "Hello! Your IP is {} and you are using {}: ".format(request.remote_addr, request.user_agent)


# @app.route('/admin/')
# def admin():
#     if not loggedin:
#         return redirect(url_for('login')) # если не залогинен, выполнять редирект на страницу входа
#     return render_template('admin.html')


@app.errorhandler(404)
def http_404_handler(error):
    return "<p>HTTP 404 Error Encountered</p>", 404

@app.errorhandler(500)
def http_500_handler(error):
    return "<p>HTTP 500 Error Encountered</p>", 500

@app.route("/error/")
def error():
    abort(404)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    posts = db.relationship('Post', backref='category')

    def __repr__(self):
        return "<{}:{}>".format(id, self.name)


post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))

    def __repr__(self):
        return "<{}:{}>".format(self.id,  self.title[:10])


class  Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    created_on  =  db.Column(db.DateTime(), default=datetime.utcnow)

    posts = db.relationship('Post', secondary=post_tags, backref='tags')

    def __repr__(self):
        return "<{}:{}>".format(id, self.name)


@app.shell_context_processor
def make_shell_context():
    import os, sys
    return dict(app=app, os=os, sys=sys)


if __name__ == "__main__":
    app.run()
