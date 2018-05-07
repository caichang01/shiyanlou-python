from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/shiyanlou'
db = SQLAlchemy(app)

mongo = MongoClient('127.0.0.1', 27017).shiyanlou

# SQLAlchemy创建文章表
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    created_time = db.Column(db.DateTime)
    content = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category',
        uselist=False,
        backref=db.backref('files', lazy='dynamic'))

    def __init__(self, title, content, category, created_time = None):
        self.title = title
        self.content = content
        if created_time is None:
            created_time = datetime.utcnow()
        self.created_time = created_time
        self.category = category

    def __repr__(self):
        return '<File %r>' % self.title

    # 向文章添加标签
    def add_tag(self, tag_name):
        file_item = mongo.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            if tag_name not in tags:
                tags.append(tag_name)
            mongo.files.update_one({'file_id': self.id}, {'$set': {'tags': tags}})
        else:
            tags = [tag_name]
            mongo.files.insert_one({'file_id': self.id, 'tags': tags}) 
        return tags

    # 移除文章标签
    def remove_tag(self, tag_name):
        file_item = mongo.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            try:
                tags.remove(tag_name)
                new_tags = tags
            except ValueError:
                return tags
            mongo.files.update_one({'file_id': self.id}, {'$set': {'tags': new_tags}})
            return new_tags
        return []

    # 标签列表
    @property
    def tags(self):
        file_item = mongo.files.find_one({'file_id': self.id})
        if file_item:
            print(file_item)
            return file_item['tags']
        else:
            return []  

# SQLAlchemy创建类别表
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.username


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
