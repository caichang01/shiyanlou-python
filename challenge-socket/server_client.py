# 导入 socket 库
import socket

# 创建一个 socket （基于IPV4协议，TCP连接）
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 建立连接
s.connect(('www.sina.com.cn', 9999))

# 发送数据
s.send(b'GET / HTTP/1.1\r\nHost: www.sina.com.cn\r\nConnection: close\r\n\r\n')

# 接受数据
buffer = []
while True:
    # 每次最多接受1k字节：
    d = s.recv(1024)
    if d:
        buffer.append(d)
    # recv() 返回为空时，接收为空，退出循环
    else:
        break
data = 'b'.join(buffer)

# 接收完毕后，关闭 socket
s.close()

# 接收到的数据包含HTTP头和网页本身，进行分离，即可将网页内容保存到文件:
header, html = data.split(b'\r\n\r\n', 1)
print(header.decode('utf-8'))
# 接收到的数据写入html文件
with open('sina.html', 'wb') as f:
    f.write(html)
