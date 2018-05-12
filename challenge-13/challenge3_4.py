import re
import pymongo


# 使用正则表达式解析日志文件， 返回数据列表
def open_parser(filename):
    with open(filename) as logfile:
        # 使用正则表达式解析日志文件
        pattern = (r''
                   r'(\d+.\d+.\d+.\d+)\s-\s-\s'  # 匹配IP地址，举例：127.0.0.1 - -
                   r'\[(.+)\]\s'  # 时间，因为时间在log中是以[]形式存在的，因此按[]形式匹配即可
                   r'"GET\s(.+)\s\w+/.+"\s'  # 匹配请求路径，本次只匹配GET请求
                   r'(\d+)\s'  # 状态码，502，200之类
                   r'(\d+)\s'  # 数据大小
                   r'"(.+)"\s'  # 请求头
                   r'"(.+)"')  # 客户端信息
        parsers = re.findall(pattern, logfile.read())
    return parsers


def main():

    # 使用正则表达式解析日志文件
    logs = open_parser('./challenge-13/nginx.log')

    # 配置mongodb
    client = pymongo.MongoClient()
    db = client.shiyanlou

    # 遍历正则表达式解析后返回的list， 创建collection，写入ip，url和状态码
    for items in logs:
        ip = items[0]
        time = items[1]
        url = items[2]
        status = items[3]
        user = {'ip': ip, 'time': time, 'url': url, 'status': status}
        db.log.insert_one(user)

    ips = db.log.find().sort([('ip', pymongo.DESCENDING)])
    ip_init = 0
    ip_dict = dict()
    url_dict = dict()
    for ipAddress in ips:
        if ipAddress['time'][:11] == '11/Jan/2017':
            if ipAddress['ip'] == ip_init:
                ip_dict[ip_init] += 1
            else:
                ip_init = ipAddress['ip']
                ip_dict[ip_init] = 1
        if ipAddress['status'] == "404":
            try:
                url_dict[ipAddress['url']] += 1
            except KeyError:
                url_dict[ipAddress['url']] = 1   # 对字典进行初始化

    ip_counts = 0
    most_frequent_ip = 0
    for key, value in ip_dict.items():
        if value > ip_counts:
            ip_counts = value
            most_frequent_ip = key
    ip_dict = dict()
    ip_dict[most_frequent_ip] = ip_counts

    url_counts = 0
    most_frequent_url = 0
    for key, value in url_dict.items():
        if value > url_counts:
            url_counts = value
            most_frequent_url = key
    url_dict = dict()
    url_dict[most_frequent_url] = url_counts

    db.drop_collection('log')

    return ip_dict, url_dict


# 执行
if __name__ == '__main__':
    print(main())
