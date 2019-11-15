from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask_login import login_required, login_user,current_user, logout_user

from app import app
from .models import User, Post, Category, db
from .forms import ContactForm, LoginForm


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