import requests
from bs4 import BeautifulSoup
import re
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 所有要抓取的 URL 列表
urls = [
    'http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'http://ip.164746.xyz',
    'https://cf.090227.xyz',
    'https://stock.hostmonit.com/CloudFlareYes'
]

ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

if os.path.exists('ip.txt'):
    os.remove('ip.txt')

all_ips = set()

# 抓取 IP 阶段
for url in urls:
    try:
        print(f"正在抓取：{url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"访问 {url} 失败：{e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(['tr', 'td', 'li', 'div', 'pre', 'code', 'p', 'span'])

    for element in elements:
        text = element.get_text()
        ip_matches = re.findall(ip_pattern, text)
        all_ips.update(ip_matches)

print(f"抓取并去重后共获得 {len(all_ips)} 个唯一 IP。")

# 测试函数，只返回延迟 ≥150ms 的 IP
def test_ip(ip):
    try:
        start = time.time()
        with socket.create_connection((ip, 443), timeout=2):
            latency = (time.time() - start) * 1000  # 毫秒
            if latency >= 150:
                return ip, latency
    except:
        return None
    return None

print("正在多线程测试 IP 连通性与延迟（只保留延迟 ≥150ms 的 IP）...")

valid_ips = []
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(test_ip, ip): ip for ip in all_ips}
    for future in as_completed(futures):
        result = future.result()
        ip = futures[future]
        if result:
            ip, latency = result
            print(f"{ip} ✅ 延迟 {latency:.2f} ms")
            valid_ips.append((ip, latency))
        else:
            print(f"{ip} ❌ 不可用或延迟过低")

# 排序
valid_ips.sort(key=lambda x: x[1])

# 保存结果
with open('ip.txt', 'w') as f:
    for ip, latency in valid_ips:
        f.write(f"{ip}  # {latency:.2f} ms\n")

print(f"\n✅ 已保存 {len(valid_ips)} 个可用 IP（延迟 ≥150ms）到 ip.txt。")
