import requests
from bs4 import BeautifulSoup
import json

for page in range(6500, 6500 + 1):
    url = f"https://www.ptt.cc/bbs/NBA/index{page}.html"  # 构建每页的URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }  # 设置请求头，模拟浏览器
    data = []
    result = requests.get(url=url, headers=headers)  # 发送请求
    result.encoding = 'utf-8'  # 设置响应编码为utf-8
    results = result.text  # 获取响应文本内容
    soup = BeautifulSoup(results, 'html.parser')  # 使用BeautifulSoup解析HTML内容
    product_divs = soup.find_all('div', class_='r-ent')  # 查找所有产品信息的div
    Data = []
    for Title in product_divs:
        data = {}

        result_title = Title.find('div', class_='title')
        if result_title and result_title.a:
            title = result_title.a.text
        else:
            title = '没有标题'
        data['标题'] = title

        popular = Title.find('div', class_= 'nrec')
        if popular and popular.span:
            popular = popular.span.text
        else:
            popular = 'N/A'
        data['人气'] = popular

        date = Title.find('div',class_='date')
        if date:
            date = date.text
        else:
            date = 'N/A'
        data['时间'] = date

        Data.append(data)

    with open('NBA快讯.json', 'w', encoding='utf-8') as file:
        json.dump(Data,file, ensure_ascii=False, indent=4)
    print('写入成功！')

    #print(Data)
    #print(f'标题: {title} ,人气: {popular} ,发布时间: {date}')
