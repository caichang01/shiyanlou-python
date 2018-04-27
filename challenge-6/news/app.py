import os
import json
from flask import Flask, render_template, abort

app = Flask(__name__)

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
    return render_template('index.html', titleList = files._getTitleList())

@app.route('/files/<filename>')
def file(filename):
    fileItem = files._getByFilename(filename)
    if not fileItem:
        abort(404)
    return render_template('file.html', fileItem = fileItem)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run