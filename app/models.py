from app import db

from datetime import datetime
from datetime import timedelta

from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
from hashlib import md5

from time import time
import jwt
from app import app



# 关联表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)



class User(UserMixin, db.Model):
    """用户表"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow )
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    


    def __repr__(self):
        return '<User {}>'.format(self.username)    


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """获取动态头像"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def now_time(self):
        """本地时间"""
        return self.last_seen + timedelta(hours=8)


    def is_following(self, user):
        """ 检查是否关注 """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        """关注"""
        if not self.is_following(user):
            self.followed.append(user)


    def unfollow(self, user):
        """取消关注"""
        if self.is_following(user):
            self.followed.remove(user)

    # def followed_posts(self):
    #     """获取关注用户的文章
        
    #     Post.query.join(...).filter(...).order_by(...)
    #     """
    #     return Post.query.join(
    #         followers, (followers.c.followed_id == Post.user_id)).filter(
    #             followers.c.follower_id == self.id).order_by(
    #                 Post.timestamp.desc())

    # def followed_posts(self):
    #     """查询自己的文章"""
    #     followed = Post.query.join(
    #         followers, (followers.c.followed_id == Post.user_id)).filter(
    #             followers.c.follower_id == self.id)
    #     own = Post.query.filter_by(user_id=self.id)
    #     return followed.union(own).order_by(Post.timestamp.desc())

    def followed_posts(self):
        """ 查询关注者的文章 """
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


    def get_reset_password_token(self, expires_in=600):
        """重置密码tocken"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        """解密"""
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    """发文表"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)        








@login.user_loader
def load_user(id):
    return User.query.get(int(id))