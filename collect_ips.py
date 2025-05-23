import requests
from bs4 import BeautifulSoup
import re
import os

urls = [
    'http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'http://ip.164746.xyz'
]

ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 删除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

with open('ip.txt', 'w') as file:
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"访问 {url} 失败: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 不管结构怎样，先尝试查找所有文字内容
        elements = soup.find_all(['tr', 'td', 'li', 'div', 'p', 'span'])

        for element in elements:
            text = element.get_text()
            ip_matches = re.findall(ip_pattern, text)
            for ip in ip_matches:
                file.write(ip + '\n')

print("IP地址已保存到 ip.txt 文件中。")
