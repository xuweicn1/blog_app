from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import EmptyForm
from app.forms import PostForm
from app.models import Post
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm
from flask import jsonify
from app.translate import translate


# 保存访问时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('index'))

    # posts = current_user.followed_posts().all()
    # return render_template("index.html", title='首页', form=form,posts=posts)

    # 分页
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for(
        'index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    """展示帖子"""
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    # return render_template('index.html', title='展示', posts=posts)
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='Home',
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():

    # 已经登陆
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():

        print(form.username.data, form.password.data)
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('错误的用户名或者密码')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='登陆', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
        flash('祝贺您,您已经是一个注册会员')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """请求重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    """用户资料"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)



    next_url = url_for('user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    # 关注状态
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """个人资料视图"""

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('保存成功.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='编辑个人资料',
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """关注"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('用户:{} 不存在'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('不能关注自己')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('您已经成功关注: {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """取消关注"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('用户:{} 不存在'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('不能关注自己')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('取消关注: {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



# @app.route('/translate', methods=['POST'])
# @login_required
# def translate_text():
#     return jsonify({'text': translate(request.form['text'],
#                                       request.form['source_language'],
#                                       request.form['dest_language'])})

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate()})