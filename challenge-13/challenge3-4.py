import re
import pymongo
from datetime import datetime

# 使用正则表达式解析日志文件， 返回数据列表
def open_parser(filename):
    with open(filename) as logfile:
        # 使用正则表达式解析日志文件
        pattern = (r''
            r'(\d+.\d+.\d+.\d+)\s-\s-\s' # 匹配IP地址，举例：127.0.0.1 - - 
            r'\[(.+)\]\s' # 时间，因为时间在log中是以[]形式存在的，因此按[]形式匹配即可
            r'"GET\s(.+)\s\w+/.+"\s' # 匹配请求路径 本次只匹配GET请求
            r'(\d+)\s' # 状态码 502，200之类
            r'(\d+)\s' # 数据大小
            r'"(.+)"\s' # 请求头
            r'"(.+)"' #客户端信息
        )
        parsers = re.findall(pattern, logfile.read())
    return parsers

def main():
    
    # 使用正则表达式解析日志文件
    logs = open_parser('C:/Users/caichang01-PC/Documents/shiyanlou-python/challenge-13/nginx.log')

    # 配置mongodb
    client = pymongo.MongoClient()
    db = client.shiyanlou

    # 遍历正则表达式解析后返回的list， 创建collection，写入ip，url和状态码
    for items in logs:
        ip = items[0]
        time = items[1]
        url = items[2]
        status =items[3]
        user = {'ip': ip, 'time': time, 'url': url, 'status': status}
        db.log.insert_one(user)
    
    ips = db.log.find().sort([('ip', pymongo.DESCENDING)])
    ipInit = 0
    ipDict = dict()
    urlDict = dict()
    for ipAddress in ips:
        if ipAddress['time'][:11] == '11/Jan/2017':
            if ipAddress['ip'] == ipInit:
                ipDict[ipInit] += 1
            else :
                ipInit = ipAddress['ip']
                ipDict[ipInit] = 1
        if ipAddress['status'] == "404":
            try:
                urlDict[ipAddress['url']] += 1
            except KeyError:
                urlDict[ipAddress['url']] = 1 # 对字典进行初始化
    
    ipCounts = 0
    mostFrequentIp = 0
    for key, value in ipDict.items():
        if value > ipCounts:
            ipCounts = value
            mostFrequentIp = key
    ipDict = dict()
    ipDict[mostFrequentIp] = ipCounts

    urlCounts = 0
    mostFrequentUrl = 0
    for key, value in urlDict.items():
        if value > urlCounts:
            urlCounts = value
            mostFrequentUrl = key
    urlDict = dict()
    urlDict[mostFrequentUrl] = urlCounts

    
    db.drop_collection('log')

    return ipDict, urlDict

# 执行
if __name__ == '__main__':
    print(main())