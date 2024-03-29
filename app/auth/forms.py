from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    """登陆表单"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住')
    submit = SubmitField('输入')


class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[DataRequired(message='请填写用户名')])
    email = StringField(
        '邮箱', validators=[DataRequired(message='请填写邮箱'), Email('邮箱格式错误')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写邮箱')])
    password2 = PasswordField(
        '重复密码', validators=[DataRequired(), EqualTo('password', message='两次输入密码要相同')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名被占用,请更换.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱被占用,请更换.')

class ResetPasswordRequestForm(FlaskForm):
    """重置密码"""
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('提交')


class ResetPasswordForm(FlaskForm):
    """新密码"""
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重置密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('提交重置')
