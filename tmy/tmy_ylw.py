"""
new Env('阅龙湾');
抓包：https://vapp.tmuyun.com/ 任意-请求头中 x-session-id 或使用 手机号#密码 两者互不影响
cron: 0 12 * * *
变量：TMUYUN_YLW='session_id=xxx' 多个账号用 & 分隔
"""
import base64
import hashlib
import json
import random
import time
import urllib
import uuid
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from env import get_env_list

APP_ID = 51
SALT = "FR*r!isE5W"

HEADER2 = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": 'Mozilla/5.0 (Linux; Android 13; POCO F2 Pro Build/TQ3A.230705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.136 Mobile Safari/537.36;xsb_longwan;xsb_longwan;1.7.5;native_app',
    'X-Requested-With': 'net.lwnews.www',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://vapp.tmuyun.com/webFunction/userCenter?tenantId=51&gaze_control=023&isCompleteSign=-1',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

REF_CODE = 'WSWHMJ'

CONTENTS = [
    "好", "支持", '赞', '越来越好'
]

CHANNEL_IDS = [
    "62c53767373c550ecabd9d6a ",
    "6327c414ad61a4052a4a2a12",
    "62c537afde224a0ebdf0fe7c",
    "62c537bc373c550ecabd9d6c",
    "63318faafe3fc1537e56b6e2",
    "62c537a1fe3fc1538430e59a"
]

PUB_KEY = """
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB
""".strip()


def encode_pwd(pwd_plain):
    public_key = RSA.import_key(base64.b64decode(PUB_KEY))
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(pwd_plain.encode())
    return base64.b64encode(ciphertext).decode()


def random_time(start=7, end=15):
    time.sleep(random.randint(start, end))


class Ylw:

    def __init__(self, phone: str, pwd: str, session=None):
        self.phone = phone
        self.pwd = pwd
        self.session_id = session
        self.account_id = ''
        self._timestamp = int(time.time() * 1000)
        self._request_id = uuid.uuid1()
        self._sign = ''
        self.mobile = ''
        self._auth_status = True
        self._integral = 0
        self._comment_ids = []
        self._shared_ids = []
        self._collect_ids = []
        self.cookie = ""
        self._signature_key = ''

    def run(self):
        try:
            self._log("==开始运行脚本==")
            if not self.init_app():
                self._log("初始化App失败，停止运行")
                return
            if not self.session_id:
                self._log("不存在session_id，使用账号密码授权")
                self.credential_auth()
            if self.session_id and self.session_id != '':
                self.account_detail()
                self.number_center()
            else:
                self._log("授权失败，请填写正确的session_id 或者账号密码")
        finally:
            self._log("==运行脚本完成==")

    def init_app(self):
        url = "https://passport.tmuyun.com/web/init?client_id=10008"

        payload = {}
        headers = {
            'Cache-Control': 'no-cache',
            'User-Agent': 'ANDROID;13;10008;1.7.5;1.0;null;POCO F2 Pro',
            'X-REQUEST-ID': str(uuid.uuid1()),
            'Connection': 'Keep-Alive'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            resp = json.loads(response.content)
            self._signature_key = resp.get('data').get('client').get('signature_key')
            return True
        return False

    def credential_auth(self):
        if not self.phone or not self.pwd:
            return
        b = {
            "client_id": "10008",
            "phone_number": self.phone
        }

        url = f"https://passport.tmuyun.com/web/account/check_phone_number?{urllib.parse.urlencode(b)}"

        uu = str(uuid.uuid1())
        headers = {
            'Cache-Control': 'no-cache',
            'User-Agent': 'ANDROID;13;10008;1.7.5;1.0;null;POCO F2 Pro',
            'X-REQUEST-ID': str(uuid.uuid1()),
            'X-SIGNATURE': self._get_sign2('get', '/web/account/check_phone_number', b, uu),
            'Connection': 'Keep-Alive',
            'Cookie': 'acw_tc=76b20ff316937358283984637e7541529591ea6463841acd587b0142257b0f',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }

        response = requests.request("GET", url, headers=headers)
        print("check = " + response.text)
        if response.status_code == 200:
            resp = json.loads(response.content)
            if resp and resp.get('code') == 0:
                if not resp.get('data').get('exist'):
                    self._log("手机号校验失败，不存在此账号")
                    return

        url = "https://passport.tmuyun.com/web/oauth/credential_auth"
        body = {
            'client_id': "10008",
            'phone_number': self.phone,
            'password': encode_pwd(self.pwd)
        }
        dict.update(headers, {
            'X-SIGNATURE': self._get_sign2('post', '/web/oauth/credential_auth', body, uu)
        })
        response = requests.post(url, data=body, headers=headers)
        print(response.text)
        if response.status_code != 200:
            self._auth_status = False
            return
        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            code = resp.get('data').get('authorization_code').get('code')
            url = "https://vapp.tmuyun.com/api/zbtxz/login"
            # TODO 网易防破解
            check_token = ''
            payload = f'check_token={check_token}&code={code}&token=&type=-1&union_id='
            headers = self._get_header("/api/zbtxz/login")
            dict.update(headers, HEADER2)
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            if response.status_code != 200:
                self._auth_status = False
                return
            resp = json.loads(response.content)
            if resp and resp.get('code') == 0:
                self.session_id = resp.get('data').get('session').get('id')

    def channel(self, ignored_read=False):
        random_time(1, 3)
        channel_id = random.choice(CHANNEL_IDS)
        url = (f"https://vapp.tmuyun.com/api/article/channel_list?channel_id={channel_id}&isDiFangHao=false"
               "&is_new=true&list_count=0&size=50")
        payload = {}
        headers = self._get_header("/api/article/channel_list")
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code != 200:
            return []

        resp = json.loads(response.content)
        result = []
        if resp and resp.get('code') == 0:
            article_list = list(resp.get('data').get('article_list'))
            for article in article_list:
                _id = article.get('id')
                content_id = article.get('content_id')
                mark_read = article.get('mark_read')
                if mark_read == 0 or ignored_read:
                    result.append(_id)

        return result

    def account_detail(self):
        self._log("【查询账号信息】")
        url = "https://vapp.tmuyun.com/api/user_mumber/account_detail"

        payload = {}
        headers = self._get_header("/api/user_mumber/account_detail")

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code != 200:
            self.account_id = ''
            return
        resp = json.loads(response.content)

        if resp and resp.get('code') == 0:
            self.account_id = resp.get('data').get('rst').get('id')
            self.phone = resp.get('data').get('rst').get('mobile')
            self._integral = resp.get('data').get('rst').get('total_integral')
            grade = resp.get('data').get('rst').get('grade')
            grade_name = resp.get('data').get('rst').get('grade_name')
            self._log("当前积分 = " + str(self._integral) + ", 等级 = " + str(grade) + "-" + grade_name)

    def number_center(self):
        url = "https://vapp.tmuyun.com/api/user_mumber/numberCenter?is_new=1"

        payload = {}
        headers = self._get_header("/api/user_mumber/numberCenter")
        dict.update(headers, HEADER2)

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code != 200:
            return

        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            bj_date_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(
                timezone(timedelta(hours=8), name='Asia/Shanghai'))
            d = bj_date_time.strftime("%Y-%m-%d")
            sign_list = list(resp.get('data').get('daily_sign_info').get('daily_sign_list'))
            for s in sign_list:
                if s.get('date') == d:
                    self._log(f"当前时间为：{d}, 是否签到 【{'是' if s.get('signed') else '否'}】")
                    if not s.get('signed'):
                        self.sign()

            user_task_list = list(resp.get('data').get('rst').get('user_task_list'))

            for task in user_task_list:
                finish_times = task.get('finish_times')
                frequency = task.get('frequency')
                task_id = task.get('id')
                member_task_type = task.get('member_task_type')
                ids = self.channel()
                if len(ids) < 0:
                    ids = self.channel(True)
                if len(ids) < 0:
                    self._log("【任务失败】为获取到可用的文章列表")
                    continue
                for i in range(finish_times, frequency):
                    self._log("【开始任务】" + task.get('name') + ", " + str(i) + "/" + str(frequency))
                    article_id = random.choice(ids)
                    if member_task_type == 2:
                        self.read(article_id)
                        random_time()
                    elif member_task_type == 3:
                        # shared
                        article_id = random.choice(ids)
                        if len(self._shared_ids) > 0:
                            article_id = self._shared_ids.pop()
                    elif member_task_type == 4:
                        article_id = random.choice(ids)
                        if len(self._comment_ids) > 0:
                            article_id = self._comment_ids.pop()
                        self.common_create(article_id)
                    elif member_task_type == 5:
                        article_id = random.choice(ids)
                        if len(self._collect_ids) > 0:
                            article_id = self._collect_ids.pop()
                        self.fav_collect(article_id)
                        self.fav_like(article_id)
                    if member_task_type == 7:
                        continue
                    self.do_task(member_task_type, str(article_id))

    def sign(self):
        self._log("【开始签到】")
        url = "https://vapp.tmuyun.com/api/user_mumber/sign"

        payload = {}
        headers = self._get_header("/api/user_mumber/sign")
        dict.update(headers, HEADER2)
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            return

        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            signExperience = resp.get('data').get('signExperience')
            self._log("签到成功: 获得积分 = " + signExperience)
        else:
            self._log("签到失败：" + resp.get('message'))

    def do_task(self, member_task_type, target_id=''):
        random_time(1, 6)
        url = "https://vapp.tmuyun.com/api/user_mumber/doTask"

        payload = f'memberType={member_task_type}&member_type={member_task_type}&target_id={target_id}'
        headers = self._get_header("/api/user_mumber/doTask")
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        requests.request("POST", url, headers=headers, data=payload)

    def read(self, article_id):
        random_time(2, 5)
        self._log("【阅读文章】" + str(article_id))
        url = f"https://vapp.tmuyun.com/api/article/detail?id={article_id}"
        payload = {}
        headers = self._get_header('/api/article/detail')
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            resp = json.loads(response.content)
            if resp and resp.get('code') == 0:
                self._shared_ids.append(article_id)
                self._collect_ids.append(article_id)
                self._comment_ids.append(article_id)

        self.read_time(article_id)

    def read_time(self, article_id):
        read_time = random.randint(150000, 20000)
        url = f"https://vapp.tmuyun.com/api/article/read_time?channel_article_id={article_id}&read_time={read_time}"
        payload = {}
        headers = self._get_header("/api/article/read_time")
        requests.request("GET", url, headers=headers, data=payload)

    def fav_like(self, article_id):
        random_time(1, 5)
        url = "https://vapp.tmuyun.com/api/favorite/like"

        payload = f'action=true&id={article_id}'
        headers = self._get_header("/api/favorite/like")
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)

    def common_create(self, article_id):
        random_time(0, 3)
        url = "https://vapp.tmuyun.com/api/comment/create"

        payload = f'channel_article_id={article_id}&content={urllib.parse.quote(random.choice(CONTENTS))}&sort_type=0'
        headers = self._get_header("/api/comment/create")
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)

    def fav_collect(self, article_id):
        random_time(0, 4)
        url = "https://vapp.tmuyun.com/api/favorite/collect"

        payload = f'action=true&id={article_id}'
        headers = self._get_header("/api/favorite/collect")
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)

    def _get_sign(self, type_id):
        self._timestamp = str(int(time.time() * 1000))
        self._request_id = str(uuid.uuid1())
        self._sign = (
            hashlib.sha256(
                f"{type_id}&&{self.session_id}&&{self._request_id}&&{self._timestamp}&&{SALT}&&{APP_ID}".encode(
                    'utf-8'))
            .hexdigest())

    def _get_sign2(self, m, url, params: dict, uu_id):
        s = f"{str(m).lower()}%%{url}"
        if len(params) > 0:
            s += "?"
            s += urllib.parse.urlencode(params)
        s += "%%" + uu_id + "%%"
        import hmac
        return hmac.new(self._signature_key.encode(), s.encode(), "sha256").hexdigest()

    def _get_header(self, type_id):
        self._get_sign(type_id)
        return {
            'X-SESSION-ID': self.session_id,
            'X-REQUEST-ID': self._request_id,
            'X-TIMESTAMP': self._timestamp,
            'X-SIGNATURE': self._sign,
            'X-TENANT-ID': str(APP_ID),
            'User-Agent': '1.7.5;00000000-646f-9305-0000-00005083af4d;Xiaomi POCO F2 Pro;Android;13;huawei',
            'X-ACCOUNT-ID': str(self.account_id),
            'Cache-Control': 'no-cache',
            'Host': 'vapp.tmuyun.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            # 'Cookie': self.cookie
        }

    def _log(self, msg):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} 【{self.phone}】: {msg}")


def main():
    accounts = get_env_list("TMUYUN_YLW")

    for account in accounts:
        phone = account.get('phone', '')
        pwd = account.get('pwd')
        _session_id = account.get("session_id")
        Ylw(phone, pwd, _session_id).run()


if __name__ == "__main__":
    main()
