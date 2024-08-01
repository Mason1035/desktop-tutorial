import requests
from bs4 import BeautifulSoup

data = []

for page in range(1, 50 + 1):
    url = f'https://www.sceea.cn/List/NewsList_{page}.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    raw_data = requests.get(url=url, headers=headers)
    raw_data.encoding = 'utf-8'  # 确保中文字符正常显示
    result = raw_data.text
    soup = BeautifulSoup(result, 'lxml')

    # 获取所有的li标签
    li_tags = soup.find_all('li')

    for li in li_tags:
        a_tag = li.find('a')
        if a_tag and a_tag.get('title'):
            href = a_tag.get('href')
            title = a_tag.get('title')
            # 获取<p>标签中的时间信息
            p_tag = li.find('p')
            time = p_tag.text.strip() if p_tag else 'No time found'
            data.append({'href': href, 'title': title, 'time': time})

# 打印提取到的数据
for item in data:
    HTTP = 'https://www.sceea.cn'
    print(f"标题: {item['title']}, 链接: " + HTTP + f"{item['href']}, 发布时间: {item['time']}")