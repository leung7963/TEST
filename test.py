import requests
import time
import socket
import socks
from requests.exceptions import RequestException

# 配置 SOCKS5 代理并测试延迟的函数
def set_socks5_proxy(proxy_ip, proxy_port, username=None, password=None):
    if username and password:
        # 使用用户名和密码进行 SOCKS5 验证
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port, username=username, password=password)
    else:
        # 不使用认证的 SOCKS5 代理
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port)
    socket.socket = socks.socksocket

def test_socks5_latency(proxy, url):
    proxy_ip, proxy_port, username, password = proxy
    try:
        # 设置代理
        set_socks5_proxy(proxy_ip, proxy_port, username, password)
        
        # 测试延迟
        start_time = time.time()
        response = requests.get(url, timeout=10)
        latency = (time.time() - start_time) * 1000  # 转换为毫秒
        print(f"Proxy {proxy_ip}:{proxy_port} -> {url}: HTTP Status Code: {response.status_code}, Latency: {latency:.2f} ms")
        return latency
    except RequestException as e:
        print(f"Proxy {proxy_ip}:{proxy_port} -> {url}: Error: {e}")
        return None

def batch_test_proxies(proxies, urls):
    results = []
    for proxy in proxies:
        for url in urls:
            latency = test_socks5_latency(proxy, url)
            results.append({"proxy": proxy, "url": url, "latency": latency})
    return results

# 代理列表 [(代理IP地址, 代理端口, 用户名, 密码)]
proxies = [
    ("", , "", "")
    #("192.168.1.102", 1080, "user2", "password2"),
    # 添加更多代理...
]

# 测试的URL列表
urls = [
    "http://www.apple.com/library/test/success.html"
    # 添加更多测试地址...
]

# 执行批量测试
results = batch_test_proxies(proxies, urls)

# 打印结果
for result in results:
    proxy_ip, proxy_port = result["proxy"][:2]  # 只获取IP和端口
    latency = result["latency"]
    print(f"Proxy {proxy_ip}:{proxy_port} -> {result['url']} Latency: {latency:.2f} ms" if latency else f"Proxy {proxy_ip}:{proxy_port} -> {result['url']} Failed")