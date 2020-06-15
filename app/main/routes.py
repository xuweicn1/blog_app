from flask import render_template, flash, redirect, url_for, request
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from flask import g
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.main import bp


# 保存访问时间  展示搜索框
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('main.index'))

    # 分页
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for(
        'main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='首页', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    """展示帖子"""
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='浏览',
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    """用户资料"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    # 关注状态
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    """弹出个人资料视图"""
    user = User.query.filter_by(username=username).first_or_404()
    print(user)
    return render_template('user_popup.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """个人资料视图"""

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('保存成功.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='编辑', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """关注"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('用户:{} 不存在'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('不能关注自己')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('您已经成功关注: {}'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """取消关注"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('用户:{} 不存在'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('不能关注自己')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('取消关注: {}'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate()})


@bp.route('/search')
@login_required
def search():
    """全文搜索"""
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='搜索', posts=posts,
                           next_url=next_url, prev_url=prev_url)
