import requests
import time
import socket
import socks
import os
from requests.exceptions import RequestException

# 配置 SOCKS5 代理并测试延迟的函数
def set_socks5_proxy(proxy_ip, proxy_port, username=None, password=None):
    if username and password:
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port, username=username, password=password)
    else:
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port)
    socket.socket = socks.socksocket



def trigger_github_action():
    # 清除全局代理设置，确保不使用代理
    socks.set_default_proxy()  # 清除之前设置的代理
    socket.socket = socks.socksocket  # 恢复原始 socket 连接

    github_token = os.environ.get("GITHUB_TOKEN")  # 从环境变量中获取 GitHub token
    repo = "leung7963/socks5-for-serv00"  # 替换为要触发的 GitHub 仓库
    workflow_id = "check_cron.yaml"  # 替换为要触发的工作流 ID 或文件名
    api_url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "ref": "main"  # 触发工作流的分支
    }
    
    try:
        # 请求 GitHub API 时不使用代理
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 204:
            print("GitHub Action triggered successfully.")
        else:
            print(f"Failed to trigger GitHub Action: {response.status_code} - {response.text}")
    except RequestException as e:
        print(f"Error triggering GitHub Action: {e}")

# 如果你需要在之后的代码里重新设置代理，可以再次调用 set_socks5_proxy


def batch_test_proxies(proxies, urls):
    failed_proxies = False  # 标志位，跟踪是否有失败的代理
    
    for proxy in proxies:
        for url in urls:
            latency = test_socks5_latency(proxy, url)
            
            proxy_ip, proxy_port = proxy[:2]  # 只获取IP和端口
            
            if latency is None:  # 如果代理连接失败
                print(f"Proxy {proxy_ip}: failed.")
                failed_proxies = True  # 设置标志位为 True
            else:
                print(f"Proxy {proxy_ip} -> {url} Latency: {latency:.2f} ms")
    
    # 所有代理测试完成后，如果有失败项，触发 GitHub Action
    if failed_proxies:
        print("Some proxies failed. Triggering GitHub Action.")
        trigger_github_action()
    else:
        print("All proxies succeeded. No need to trigger GitHub Action.")

# 从环境变量中读取代理信息并解析
def load_proxies_from_env():
    proxy_data = os.environ.get("PROXY_DATA", "")
    proxies = []
    for line in proxy_data.splitlines():
        line = line.strip()  # 移除换行符和多余的空白
        if line:
            try:
                user_pass, ip_port = line.split('@')
                username, password = user_pass.split(':')
                ip, port = ip_port.split(':')
                proxies.append((ip, int(port), username, password))
            except ValueError:
                print(f"Skipping invalid proxy entry: {line}")
    return proxies

# 测试的URL列表
urls = [
    "http://cp.cloudflare.com/"
]

# 从环境变量中加载代理
proxies = load_proxies_from_env()

# 执行批量测试
batch_test_proxies(proxies, urls)