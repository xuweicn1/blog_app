from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """检查密码 获取token """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    """校验token"""
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    """错误指向"""
    return error_response(status)