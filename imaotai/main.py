import datetime
import json
import logging
import math
import os
import random
import re
import time
import uuid

import requests

from imaotai import config
from imaotai.encrypt import Encrypt

AES_KEY = 'qbhajinldepmucsonaaaccgypwuvcjaa'
AES_IV = '2018534749963515'
SALT = '2af72f100c356273d46284f6fd1dfc08'

GMT = "%a %b %d %H:%M:%S GMT+08:00 %Y"
mt_version = "1.4.6"
mt_r = "clips_OlU6TmFRag5rCXwbNAQ/Tz1SKlN8TXYfcRt+HWlGdg=="

headers = {
    'MT-K': '1693444419804',
    'MT-V': '2db7075382c8b685b4f47ae5a3r',
    'MT-Info': '028e7f96f6369cafe1d105579c5b9377',
    'MT-Token': '',
    'User-Agent': 'android;33;Xiaomi;sagit',
    'MT-Device-ID': 'clips_f0Z3Q3YTd0MhQHgaKEpzQCQTIEUkESQTcEYnEScTIA==',
    'MT-APP-Version': mt_version,
    'MT-Request-ID': 'fcd0c062-8a06-4d84-8c52-486cc748481e',
    'MT-Network-Type': 'WIFI',
    'MT-R': mt_r,
    'MT-Bundle-ID': 'com.moutai.mall',
    'MT-USER-TAG': '0',
    'MT-SN': 'clips_ehwpSC0fLBggRnJAdxYgFiAYLxl9Si5PfEl/TC0afkw=',
    'MT-DTIME': 'Sun Mar 26 20:52:19 GMT+08:00 2023',
    'MT-RS': '1080*1852',
    'MT-Lng': '119.234554',
    'MT-Lat': '26.062803',
    'BS-DVID': '',  # l6dF6GXKXeKZuYm-wJ21lpkfodHj-bvWR9RERut-vEiQ6U7hbbPMmgXlm2mnPvb5Rv5J2SsZRcThiUdvb7Xwaqg
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

account_dicts = []


def _init_headers(user_id: str, token: str, lat: str = '28.499562', lng: str = '102.182324'):
    dict.update(headers, {"userId": user_id})
    dict.update(headers, {"MT-Token": token})
    dict.update(headers, {"MT-Lat": lat})
    dict.update(headers, {"MT-Lng": lng})
    dict.update(headers, {"MT-APP-Version": mt_version})
    _update_header()


def _update_header():
    dict.update(headers, {"MT-DTIME": datetime.datetime.now().strftime(GMT)})
    dict.update(headers, {"MT-Request-ID": str(uuid.uuid1())})


def get_current_session_id():
    day_time = int(time.mktime(datetime.date.today().timetuple())) * 1000
    responses = requests.get(f"https://static.moutai519.com.cn/mt-backend/xhr/front/mall/index/session/get/{day_time}")
    if responses.status_code != 200:
        print(f"请求sessionId失败，{responses.status_code}: {responses.text}")
    current_session_id = responses.json()['data']['sessionId']
    dict.update(headers, {'current_session_id': str(current_session_id)})


def _send(msg):
    try:
        from sendNotify import send
        send("I茅台", msg)
    except:
        print(f"通知失败，通知模块不存在: {msg}")


def get_location_count(province: str, city: str, item_code: str, p_c_map: dict,
                       source_data: dict, lat: str, lng: str):
    day_time = int(time.mktime(datetime.date.today().timetuple())) * 1000
    session_id = headers['current_session_id']
    responses = requests.get(
        f"https://static.moutai519.com.cn/mt-backend/xhr/front/mall/shop/list/slim/v3/{session_id}/{province}/{item_code}/{day_time}")
    if responses.status_code != 200:
        print(
            f'get_location_count : params : {day_time}, response code : {responses.status_code}, response body : {responses.text}')
    shops = responses.json()['data']['shops']

    if config.MAX_ENABLED:
        return max_shop(city, item_code, p_c_map, province, shops)
    if config.DISTANCE_ENABLED:
        return distance_shop(city, item_code, p_c_map, province, shops, source_data, lat, lng)


def max_shop(city, item_code, p_c_map, province, shops):
    max_count = 0
    max_shop_id = '0'
    shop_ids = p_c_map[province][city]
    for shop in shops:
        shopId = shop['shopId']
        items = shop['items']

        if shopId not in shop_ids:
            continue
        for item in items:
            if item['itemId'] != str(item_code):
                continue
            if item['inventory'] > max_count:
                max_count = item['inventory']
                max_shop_id = shopId
    print(f'item code {item_code}, max shop id : {max_shop_id}, max count : {max_count}')
    return max_shop_id


def distance_shop(city,
                  item_code,
                  p_c_map,
                  province,
                  shops,
                  source_data,
                  lat: str = '28.499562',
                  lng: str = '102.182324'):
    # shop_ids = p_c_map[province][city]
    temp_list = []
    for shop in shops:
        shopId = shop['shopId']
        items = shop['items']
        item_ids = [i['itemId'] for i in items]
        # if shopId not in shop_ids:
        #     continue
        if str(item_code) not in item_ids:
            continue
        shop_info = source_data.get(shopId)
        # d = geodesic((lat, lng), (shop_info['lat'], shop_info['lng'])).km
        d = math.sqrt((float(lat) - shop_info['lat']) ** 2 + (float(lng) - shop_info['lng']) ** 2)
        # print(f"距离：{d}")
        temp_list.append((d, shopId))

    # sorted(a,key=lambda x:x[0])
    temp_list = sorted(temp_list, key=lambda x: x[0])
    # logging.info(f"所有门店距离:{temp_list}")
    if len(temp_list) > 0:
        return temp_list[0][1]
    else:
        return '0'


_encrypt = Encrypt(key=AES_KEY, iv=AES_IV)


def act_params(shop_id: str, item_id: str):
    # {
    #     "actParam": "a/v0XjWK/a/a+ZyaSlKKZViJHuh8tLw==",
    #     "itemInfoList": [
    #         {
    #             "count": 1,
    #             "itemId": "2478"
    #         }
    #     ],
    #     "shopId": "151510100019",
    #     "sessionId": 508
    # }
    session_id = headers['current_session_id']
    userId = headers['userId']
    params = {"itemInfoList": [{"count": 1, "itemId": item_id}],
              "sessionId": int(session_id),
              "userId": userId,
              "shopId": shop_id
              }
    s = json.dumps(params)
    act = _encrypt.aes_encrypt(s)
    params.update({"actParam": act})
    return params


def reservation(params: dict, mobile: str):
    params.pop('userId')
    _update_header()
    responses = requests.post("https://app.moutai519.com.cn/xhr/front/mall/reservation/add",
                              json=params, headers=headers)
    if responses.status_code == 401:
        print(f'[{mobile}],登录token失效，需要重新登录')
        return "登录token失效，需要重新登录"
    if '您的实名信息未完善或未通过认证' in responses.text:
        print(f'[{mobile}],{responses.text}')
        return "您的实名信息未完善或未通过认证"
    print(
        f'预约 : mobile:{mobile} :  response code : {responses.status_code}, response body : {responses.text}')

    return responses.text


def select_geo(i: str):
    # https://www.piliang.tech/geocoding-amap
    resp = requests.get(f"https://www.piliang.tech/api/amap/geocode?address={i}")
    geocodes: list = resp.json()['geocodes']
    return geocodes


def get_map(lat: str, lng: str):
    p_c_map = {}
    url = 'https://static.moutai519.com.cn/mt-backend/xhr/front/mall/resource/get'
    res = requests.get(url, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X)',
        'Referer': 'https://h5.moutai519.com.cn/gux/game/main?appConfig=2_1_2',
        'MT-R': mt_r,
        'Origin': 'https://h5.moutai519.com.cn',
        'MT-APP-Version': mt_version,
        'MT-Request-ID': f'{int(time.time() * 1000)}{random.randint(1111111, 999999999)}{int(time.time() * 1000)}',
        'Accept-Language': 'zh-CN,zh-Hans;q=1',
        'MT-Device-ID': f'{int(time.time() * 1000)}{random.randint(1111111, 999999999)}{int(time.time() * 1000)}',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'mt-lng': f'{lng}',
        'mt-lat': f'{lat}'
    })
    mtshops = res.json().get('data', {}).get('mtshops_pc', {})
    urls = mtshops.get('url')
    r = requests.get(urls)
    for k, v in dict(r.json()).items():
        province_name = v.get('provinceName')
        city_name = v.get('cityName')
        if not p_c_map.get(province_name):
            p_c_map[province_name] = {}
        if not p_c_map[province_name].get(city_name, None):
            p_c_map[province_name][city_name] = [k]
        else:
            p_c_map[province_name][city_name].append(k)

    return p_c_map, dict(r.json())


def get_user_energy_award(mobile: str):
    """
    领取耐力
    """
    cookies = {
        'MT-Device-ID-Wap': headers['MT-Device-ID'],
        'MT-Token-Wap': headers['MT-Token'],
        'YX_SUPPORT_WEBP': '1',
    }
    response = requests.post('https://h5.moutai519.com.cn/game/isolationPage/getUserEnergyAward', cookies=cookies,
                             headers=headers, json={})
    # response.json().get('message') if '无法领取奖励' in response.text else "领取奖励成功"
    print(
        f'领取耐力 : mobile:{mobile} :  response code : {response.status_code}, response body : {response.text}')


def check_login():
    _update_header()
    response = requests.get("https://app.moutai519.com.cn/xhr/front/user/info", headers=headers)
    is_login = response.status_code == 200
    print(f"检查账号是否登录: {'已登录' if is_login else 'token失效'}")
    return is_login


PHONE_KEY = "phone"
PROVINCE_KEY = "province"
CITY_KEY = "city"
TOKEN_KEY = "token"
USER_ID_KEY = "userId"
LAT_KEY = "lat"
LNG_KEY = "lng"


def _init_account():
    global account_dicts
    account_dicts = []
    imaotai = os.environ.get("IMAOTAIS")
    if imaotai:
        imaotai = str(imaotai)
        accounts = imaotai.split("&")
        for account in accounts:
            account = str(account)
            params = account.split(";")
            account_dict = {}
            if not params or len(params) < 7:
                continue
            for param in params:
                kv = param.split("=")
                if not kv or len(kv) < 2:
                    continue
                k, v = kv
                account_dict[k] = v

            if len(account_dict) > 0:
                account_dicts.append(account_dict)

    print(f"====================共{len(account_dicts)}个I茅台账号=========\n")
    print(f"==========脚本执行- 北京时间(UTC+8)：{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}============\n")


def main():
    _init_account()
    get_current_session_id()
    global account_dicts
    send_msg = ""
    for account in account_dicts:
        phone = account.get(PHONE_KEY)
        try:
            province = account.get(PROVINCE_KEY)
            city = account.get(CITY_KEY)
            token = account.get(TOKEN_KEY)
            user_id = account.get(USER_ID_KEY)
            lat = account.get(LAT_KEY)
            lng = account.get(LNG_KEY)
            _init_headers(user_id, token, lat, lng)

            p_c_map, source_data = get_map(lat=lat, lng=lng)
            is_login = check_login()

            send_msg += f"\n账号{phone} 是否登录: {is_login}\n"
            if not is_login:
                continue

            for item in config.ITEM_CODES:
                max_shop_id = get_location_count(province=province,
                                                 city=city,
                                                 item_code=item,
                                                 p_c_map=p_c_map,
                                                 source_data=source_data,
                                                 lat=lat,
                                                 lng=lng)
                print(f'max shop id : {max_shop_id}')
                if max_shop_id == '0':
                    continue
                shop_info = source_data.get(str(max_shop_id))
                title = config.ITEM_MAP.get(item)
                print(f'商品：{title}, 门店：{shop_info["name"]}')
                reservation_params = act_params(max_shop_id, item)
                txt = reservation(reservation_params, phone)
                send_msg += f'商品：{title} \n 门店：{shop_info["name"]} \n预约: {txt} \r\n\n'
                get_user_energy_award(phone)
            _send(send_msg)
        except Exception as e:
            print(e)
            _send(f"账号{phone}执行失败, {str(e)}")


if __name__ == "__main__":
    main()
    pass
