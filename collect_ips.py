import requests
from bs4 import BeautifulSoup
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 待抓取的 URL
urls = [
    'http://monitor.gacjie.cn/page/cloudflare/ipv4.html',
    'http://ip.164746.xyz',
    'https://cf.090227.xyz',
    'https://stock.hostmonit.com/CloudFlareYes'
]

ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

# 清除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

all_ips = set()

# 第一步：抓取 IP
for url in urls:
    try:
        print(f"正在抓取：{url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ 无法访问 {url}：{e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all(['tr', 'td', 'li', 'div', 'pre', 'code', 'p', 'span'])

    for element in elements:
        text = element.get_text()
        ip_matches = re.findall(ip_pattern, text)
        all_ips.update(ip_matches)

print(f"\n✅ 共抓取并去重出 {len(all_ips)} 个唯一 IP，开始测试...\n")

# 第二步：测试 IP 是否支持访问并测延迟
def test_ip(ip):
    test_url = f"https://{ip}/generate_204"
    headers = {
        "Host": "cp.cloudflare.com"
    }
    try:
        start = time.time()
        response = requests.get(test_url, headers=headers, timeout=3, verify=False)
        latency = (time.time() - start) * 1000
        if response.status_code == 204 and latency >= 150:
            return ip, latency
    except:
        pass
    return None

# 使用线程池加速
valid_ips = []
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(test_ip, ip): ip for ip in all_ips}
    for future in as_completed(futures):
        result = future.result()
        if result:
            ip, latency = result
            print(f"✅ {ip} 响应正常，延迟 {latency:.2f}ms")
            valid_ips.append((ip, latency))
        else:
            ip = futures[future]
            print(f"❌ {ip} 无法使用或延迟过低")

# 保存结果
with open('ip.txt', 'w') as f:
    for ip, latency in valid_ips:
        f.write(f"{ip}  # 延迟: {latency:.2f}ms\n")

print(f"\n🎉 测试完成，共保留 {len(valid_ips)} 个可用 IP，已写入 ip.txt")
