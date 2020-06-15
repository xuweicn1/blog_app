# from flask_wtf import FlaskForm
# from wtforms import StringField, TextAreaField,PasswordField, BooleanField, SubmitField
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo ,Length
# from app.models import User


from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


class EditProfileForm(FlaskForm):
    """个人资料表单"""
    username = StringField('用户名', validators=[DataRequired()])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('输入')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('用户被占用,请重新输入')


class EmptyForm(FlaskForm):
    """ 提交按钮 """
    submit = SubmitField('确定')


class PostForm(FlaskForm):
    """发文章"""
    post = TextAreaField('说说:', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('提交')


class SearchForm(FlaskForm):
    """全文搜索"""
    q = StringField('搜索', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)