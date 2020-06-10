# blog_app

博客站


'''
pip install flask-sqlalchemy -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install flask-migrate -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install flask-wtf
'''



```python
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run

flask db init
flask db migrate
flask db upgrade
```