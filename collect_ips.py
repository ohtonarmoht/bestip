import requests
from bs4 import BeautifulSoup
import re
import os

# 所有要抓取的 URL 列表（全部改为 http 或 https 正确形式）
urls = [
    'http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'http://ip.164746.xyz',
    'https://cf.090227.xyz',
    'https://stock.hostmonit.com/CloudFlareYes'
]

# 正则匹配 IPv4
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

# 删除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            print(f"正在抓取：{url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"访问 {url} 失败：{e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有有可能包含 IP 的标签
        elements = soup.find_all(['tr', 'td', 'li', 'div', 'pre', 'code', 'p', 'span'])

        found = 0
        for element in elements:
            text = element.get_text()
            ip_matches = re.findall(ip_pattern, text)
            for ip in ip_matches:
                file.write(ip + '\n')
                found += 1

        print(f"从 {url} 抓取到 {found} 个 IP。")

print("所有 IP 已保存到 ip.txt。")
