import socket
import threading
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 监听端口，小于 1024 的端口必须有管理员权限才能绑定:
s.bind(('127.0.0.1', 9999))
# 调用 listen 方法，传入参数代表指定等待连接的最大数量
s.listen(5)
print('Waiting for connection...')


# 每个连接都必须基于新的线程或进程
def tcplink(sock, addr):
    print('Accept new connection from %s:%s...' % addr)
    sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        time.sleep(1)
        if not data or data.decode('utf-8') == 'exit':
            break
        sock.send(('Hello, %s!' % data.decode('utf-8')).encode('utf-8'))
    sock.close()
    print('Connection from %s:%s closed.' % addr)


# 服务器在一个永久循环中接收来自客户端的连接， accept() 会等待并返回一个客户端的连接
while True:
    # 接受一个新连接
    sock, addr = s.accept()
    # 创建新线程处理 TCP 连接
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()



