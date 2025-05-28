import requests
from bs4 import BeautifulSoup
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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

# 使用真实 HTTP 请求测试 IP 延迟
def test_ip(ip):
    test_url = f"https://{ip}/generate_204"
    headers = {
        "Host": "www.gstatic.com"
    }
    try:
        start = time.time()
        response = requests.get(test_url, headers=headers, timeout=3, verify=False)
        latency = (time.time() - start) * 1000
        if response.status_code == 204 and latency >= 150:
            return ip, latency
        else:
            print(f"{ip} ❌ 状态码 {response.status_code} 或延迟 {latency:.2f} ms 过低")
    except Exception as e:
        print(f"{ip} ❌ 请求失败：{e}")
    return None

print("正在多线程真实请求测试 IP（保留延迟 ≥150ms 的）...")

valid_ips = []
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(test_ip, ip): ip for ip in all_ips}
    for future in as_completed(futures):
        result = future.result()
        if result:
            ip, latency = result
            print(f"{ip} ✅ 延迟 {latency:.2f} ms")
            valid_ips.append((ip, latency))

valid_ips.sort(key=lambda x: x[1])

with open('ip.txt', 'w') as f:
    for ip, latency in valid_ips:
        f.write(f"{ip}  # {latency:.2f} ms\n")

print(f"\n✅ 已保存 {len(valid_ips)} 个可用 IP（真实请求，延迟 ≥150ms）到 ip.txt。")
