from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user,logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': '张无忌'}
    posts = [
        {
            'author': {'username': '张三'},
            'body': '最近上映的电影<< 哪吒 >>很好看'
        },
        {
            'author': {'username': '李四'},
            'body': '我也看过,确实不错'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)



@app.route('/login', methods=['GET', 'POST'])
def login():

    # 已经登陆
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('错误的用户名或者密码')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html', title='登陆', form=form)




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))