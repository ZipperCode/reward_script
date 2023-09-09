import json
import time

import requests
"""
client_id = 10
app_name = 和合天台
client_id = 11
app_name = 今日南浔
client_id = 12
app_name = 诗画浦江
client_id = 14
app_name = 魅力金海
client_id = 15
app_name = 金沙融媒
client_id = 16
app_name = 锦绣织金
client_id = 17
app_name = 仑传
client_id = 18
app_name = 爱常山
client_id = 25
app_name = 珙桐纳雍
client_id = 27
app_name = 指尖丽水
client_id = 28
app_name = 柯桥通
client_id = 29
app_name = 掌上温岭
client_id = 32
app_name = 纳雍-测试
client_id = 33
app_name = 定海山
client_id = 34
app_name = 新府城
client_id = 35
app_name = 多娇江山
client_id = 37
app_name = 爱嵊州
client_id = 38
app_name = 爱上吴兴
client_id = 39
app_name = 目光资讯 
client_id = 40
app_name = i-Port
client_id = 41
app_name = 看岱山
client_id = 42
app_name = 运动柯城
client_id = 43
app_name = 掌上鹿城
client_id = 45
app_name = 融磐安
client_id = 47
app_name = 中国畲乡
client_id = 48
app_name = 今日越城
client_id = 49
app_name = 无线临海
client_id = 50
app_name = 西施眼客户端
client_id = 51
app_name = 爱平阳
client_id = 52
app_name = 瞄电影
client_id = 54
app_name = 永康新闻
client_id = 56
app_name = 浙农号
client_id = 58
app_name = 乐音清扬
client_id = 59
app_name = 橘传媒
client_id = 62
app_name = 上虞百观新闻
"""

def get_app(client_id):
    url = f"https://passport.tmuyun.com/web/init?client_id={client_id}"

    payload = {}
    headers = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'ANDROID;13;10008;1.7.5;1.0;null;POCO F2 Pro',
        'X-REQUEST-ID': 'f5404dda-d7a5-45a1-9ee5-b8913a81cb68',
        'Connection': 'Keep-Alive',
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            print("client_id = " + str(resp.get('data').get('client').get('client_id')))
            print("app_name = " + str(resp.get('data').get('client').get('app_name')))


if __name__ == '__main__':
    for i in range(1, 1000):
        time.sleep(3)
        get_app(i)