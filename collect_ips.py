import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表（注意全部为 http 而不是 https）
urls = ['http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
        'http://ip.164746.xyz']

# 正则表达式用于匹配IP地址
ip_pattern = r'\b\d{1,3}(?:\.\d{1,3}){3}\b'

# 如果存在旧的 ip.txt 文件则删除
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建新文件保存IP地址
with open('ip.txt', 'w') as file:
    for url in urls:
        print(f"正在请求：{url}")
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            response.raise_for_status()  # 如果不是 2xx 响应，将抛出异常
        except Exception as e:
            print(f"请求失败：{url}，错误：{e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # 默认结构：先用 <tr>，找不到就 fallback 到 <li>
        elements = soup.find_all('tr')
        if not elements:
            elements = soup.find_all('li')

        count = 0
        for element in elements:
            element_text = element.get_text()
            ip_matches = re.findall(ip_pattern, element_text)
            for ip in ip_matches:
                file.write(ip + '\n')
                count += 1

        print(f"从 {url} 提取到 {count} 个 IP 地址")

print('IP地址已保存到 ip.txt 文件中。')
