import requests
from bs4 import BeautifulSoup
import re
import os

# 所有要抓取的 URL 列表
urls = [
    'http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'http://ip.164746.xyz'
]

# 正则匹配 IPv4
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

# 删除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 抓取 IP 并写入文件
all_ips = []

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

    found = 0
    for element in elements:
        text = element.get_text()
        ip_matches = re.findall(ip_pattern, text)
        for ip in ip_matches:
            all_ips.append(ip)
            found += 1

    print(f"从 {url} 抓取到 {found} 个 IP。")

# 去重并排序
unique_ips = sorted(set(all_ips), key=lambda x: list(map(int, x.split('.'))))

# 写入文件
with open('ip.txt', 'w') as file:
    for ip in unique_ips:
        file.write(ip + '\n')

print(f"已保存 {len(unique_ips)} 个唯一 IP 到 ip.txt。")
