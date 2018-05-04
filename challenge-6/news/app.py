import os
import json
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/shiyanlou'
db = SQLAlchemy(app)

# SQLAlchemy创建文章表
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    created_time = db.Column(db.Datetime)
    content = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('files', lazy='dynamic'))

    def __init__(self, title, content, category, created_time = None):
        self.id = id
        self.title = title
        if created_time is None:
            created_time = datetime.utcnow()
        self.created_time = created_time
        self.category = category

    def __repr__(self):
        return '<File %r>' % self.title

# SQLAlchemy创建类别表
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.username

# 定义文件处理类
class Files(object):

    # 使用os.path模块确定新闻文件路径
    directory = os.path.join(os.path.abspath(os.path.dirname(__name__)), '..', 'files')

    def __init__(self):
        self._files = self._readAllFile()

    # 定义_readAllFile方法，读取两个json文件
    def _readAllFile(self):
        result={}
        for filename in os.listdir(self.directory):
            filepath = os.path.join(self.directory, filename)
            with open(filepath) as file:
                # 使用json模块
                result[filename[:-5]] = json.load(file)
            # 返回result字典
        return result

    # 定义_getTitleList方法，获取新闻标题
    def _getTitleList(self):
        return [item['title'] for item in self._files.values()]

    # 定义_getByFilename方法，使用标题检索新闻
    def _getByFilename(self, filename):
        return self._files.get(filename)

files = Files()

@app.route('/')
def index():
    return render_template('index.html', files = File.query.all())

@app.route('/files/<int:file_id>')
def file(file_id):
    file_item = File.query.get_or_404(file_id)
    return render_template('file.html', file_item =file_item)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run