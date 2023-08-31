import datetime
import hashlib
import logging
import re
import time
import uuid

import requests


def select_geo(i: str):
    # https://www.piliang.tech/geocoding-amap
    resp = requests.get(f"https://www.piliang.tech/api/amap/geocode?address={i}")
    geocodes: list = resp.json()['geocodes']
    return geocodes


def get_location():
    while 1:

        location = input(f"请输入你的位置，例如[小区名称]，为你自动预约附近的门店:").lstrip().rstrip()
        selects = select_geo(location)

        a = 0
        for item in selects:
            formatted_address = item['formatted_address']
            province = item['province']
            print(f'{a} : [地区:{province},位置:{formatted_address}]')
            a += 1
        user_select = input(f"请选择位置序号,重新输入请输入[-]:").lstrip().rstrip()
        if user_select == '-':
            continue
        select = selects[int(user_select)]
        formatted_address = select['formatted_address']
        province = select['province']
        print(f'已选择 地区:{province},[{formatted_address}]附近的门店')
        return select


# User-Agent 生成规则 android;[sdk版本];[厂商];[型号]
# MT-Device-ID 生成规则 获取设备ID(UUID) 转换为字节后每一位异或后转base64，并添加前缀clips_
# MT-Request-ID UUID
# MT-R 生成规则 root/0;debug/0;proxy/0;inject/0 每一位异或后转base64 并添加前缀clips_
# MT-SN 包签名的Md5值，一般固定 clips_ehwpSC0fLBggRnJAdxYgFiAYLxl9Si5PfEl/TC0afkw=

headers = {
    'MT-Token': '',
    'User-Agent': 'android;33;Xiaomi;sagit',
    'MT-Device-ID': 'clips_f0Z3Q3YTd0MhQHgaKEpzQCQTIEUkESQTcEYnEScTIA==',
    'MT-APP-Version': '1.4.6',
    'MT-Request-ID': '26593c76-37ee-4039-893e-8d2d50c90fd2',
    'MT-Network-Type': 'WIFI',
    'MT-R': 'clips_OlU6TmFRag5rCXwbNAQ/Tz1SKlN8TXYfcRt+HWlGdg==',
    'MT-Bundle-ID': 'com.moutai.mall',
    'MT-USER-TAG': '0',
    'MT-SN': 'clips_ehwpSC0fLBggRnJAdxYgFiAYLxl9Si5PfEl/TC0afkw=',
    'MT-DTIME': 'Sun Mar 26 20:52:19 GMT+08:00 2023',
    'MT-RS': '1080*1852',
    'MT-Lng': '',
    'MT-Lat': '',
    'BS-DVID': '',  # l6dF6GXKXeKZuYm-wJ21lpkfodHj-bvWR9RERut-vEiS6jvE0U6BJ5NJZ5sJ1QVtM83f155gQFInUjUtmS7Vz0w
    'MT-DOUBLE': '0',
    'MT-SIM': '0',
    'MT-ACBE': '0',
    'MT-ACB': '0',
    'MT-ACBM': '0',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'app.moutai519.com.cn',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
}

mt_version = "1.4.6"

GMT = "%a %b %d %H:%M:%S GMT+08:00 %Y"


def update_header():
    dict.update(headers, {"MT-DTIME": datetime.datetime.now().strftime(GMT)})
    dict.update(headers, {"MT-Request-ID": str(uuid.uuid1())})


def signature(data: dict, t):
    keys = sorted(data.keys())
    temp_v = ''
    for item in keys:
        temp_v += data[item]
    text = "2af72f100c356273d46284f6fd1dfc08" + temp_v + str(t)
    hl = hashlib.md5()
    hl.update(text.encode(encoding='utf8'))
    md5 = hl.hexdigest()
    return md5


def get_vcode(mobile: str):
    params = {'mobile': mobile}
    t = str(int(time.time() * 1000))
    md5 = signature(params, t)
    dict.update(params, {'md5': md5, "timestamp": t, 'MT-APP-Version': mt_version})
    update_header()
    responses = requests.post("https://app.moutai519.com.cn/xhr/front/user/register/vcode", json=params,
                              headers=headers)
    if responses.status_code != 200:
        logging.info(
            f'get v_code : params : {params}, response code : {responses.status_code}, response body : {responses.text}')

    print(f"get_v_code: {responses.text}")


def login(mobile: str, v_code: str):
    params = {'mobile': mobile, 'vCode': v_code, 'ydToken': '', 'ydLogId': ''}
    t = str(int(time.time() * 1000))
    md5 = signature(params, t)
    dict.update(params, {'md5': md5, "timestamp": t, 'MT-APP-Version': mt_version})
    responses = requests.post("https://app.moutai519.com.cn/xhr/front/user/register/login", json=params,
                              headers=headers)
    if responses.status_code != 200:
        logging.info(
            f'login : params : {params}, response code : {responses.status_code}, response body : {responses.text}')
    dict.update(headers, {'MT-Token': responses.json()['data']['token']})
    dict.update(headers, {'userId': responses.json()['data']['userId']})
    return responses.json()['data']['token'], responses.json()['data']['userId']


if __name__ == '__main__':

    while 1:
        location_select: dict = get_location()
        province = location_select['province']
        city = location_select['city']
        location: str = location_select['location']
        print("province = " + str(province))
        print("city = " + str(city))
        print("lat = " + str(location.split(',')[1]))
        print("lng = " + str(location.split(',')[0]))
        mobile = input("输入手机号[13812341234]:").lstrip().rstrip()
        get_vcode(mobile)
        code = input(f"输入 [{mobile}] 验证码[1234]:").lstrip().rstrip()
        token, userId = login(mobile, code)

        lat = location.split(',')[1]
        lng = location.split(',')[0]

        text = f"phone={mobile};token={token};userId={userId};province={province};city={city};lat={lat};lng={lng}"
        print(f"账号添加成功: 【{text}】")

        condition = input(f"是否继续添加账号[Y/N]:").lstrip().rstrip()
        condition = condition.lower()
        if condition == 'n':
            break
