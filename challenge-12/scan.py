import sys
import socket
from getopt import getopt, GetoptError

# 命令行参数处理
def get_args():
    try:
        opts, _ = getopt(sys.argv[1:], 'h:p:', ['host=', 'port='])
    except GetoptError:
        print('Parameter Error')
        exit()
    options = dict(opts)
    
    # 判断IP地址参数是否正常
    if len(options['--host'].split('.')) != 4:
        print('IP address Error!')
        exit()
    else:
        hostList = [options['--host']]

    # 判断是否是多端口测试
    if '-' in  options['--port']:
        portList = options['--port'].split('-')
    else:
        portList = [options['--port'], options['--port']]
    
    return hostList, portList

# 端口扫描
def scan():
    host = get_args()[0]
    port = get_args()[1]
    # 创建list，用于存储检测到开启的端口号
    openPortList = []
    # 扫描端口
    for i in range(int(port[0]), int(port[1]) + 1):
        # 创建 socket 对象
        s = socket.socket()
        # 设置超时，防止脚本卡住
        s.settimeout(0.1)
        if s.connect_ex((host[0], i)) == 0:
            openPortList.append(i)
            print(i, 'open')
        else:
            print(i, 'closed')
        s.close()
    # 输出处于开启状态的端口
    print(f'Scanning accomplished. Opening ports at {openPortList}')

# 执行
if __name__ == '__main__':
    scan()