import base64
import hashlib
import json
import random
import time
import urllib
import uuid
from abc import ABCMeta
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

SALT = "FR*r!isE5W"
USER_AGENT_PREFIX = ";00000000-646f-9305-ffff-ffffd01e6034;Xiaomi POCO F2 Pro;Android;13;Release"

CONTENTS = [
    "好", "支持", '赞', '越来越好', '好活动', '太幸福了吧', '打卡', "加油", '积极点赞', '积极参与'
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


class TmuYun(metaclass=ABCMeta):
    app_id = 0
    package_name = ''
    app_version = ''
    channel_ids = []
    _user_agent = app_version + USER_AGENT_PREFIX
    ref_core = ''

    def __init__(self, session, is_invite=True, ):

        self.session_id = session
        self.account_id = ''
        self.is_invite = is_invite
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
        self.ref_code = ''

    def run(self):
        try:
            self._log("==开始运行==")
            if self.session_id and self.session_id != '':
                self.get_version()
                if self.account_detail():
                    self.number_center()
                self.account_detail()

                self.invite()
            else:
                self._log("授权失败，请填写正确的session_id 或者账号密码")
        finally:
            self._log("==运行完成==")

    def channel(self, ignored_read=False):
        random_time(1, 3)
        channel_id = random.choice(TmuYun.channel_ids)
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
            return False
        resp = json.loads(response.content)

        if resp and resp.get('code') == 0:
            self.account_id = resp.get('data').get('rst').get('id')
            self.mobile = resp.get('data').get('rst').get('mobile')
            try:
                self.account_id = resp.get('data').get('rst').get('id')
                self._integral = resp.get('data').get('rst').get('total_integral')
                grade = resp.get('data').get('rst').get('grade')
                grade_name = resp.get('data').get('rst').get('grade_name')
                self.ref_code = resp.get('data').get('rst').get('ref_code')
                self._log("当前积分 = " + str(self._integral) + ", 等级 = " + str(grade) + "-" + grade_name)
            except:
                self._log("没有积分等级数据")
            finally:
                return True
        else:
            self._log("失败，" + resp.get('message'))
            return False

    def number_center(self):
        url = "https://vapp.tmuyun.com/api/user_mumber/numberCenter?is_new=1"
        payload = {}
        headers = self._get_header("/api/user_mumber/numberCenter")
        dict.update(headers, self._get_header2())
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            return

        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            try:
                bj_date_time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(
                    timezone(timedelta(hours=8), name='Asia/Shanghai'))
                d = bj_date_time.strftime("%Y-%m-%d")
                sign_list = list(resp.get('data').get('daily_sign_info').get('daily_sign_list'))
                for s in sign_list:
                    if s.get('current') == '今天':
                        self._log(f"当前时间为：{d}, 是否签到 【{'是' if s.get('signed') else '否'}】")
                        if not s.get('signed'):
                            self.sign()
            except:
                self._log("可能没有日常签到流程")
                self.sign()
            user_task_list = self.get_task_list(resp.get('data').get('rst').get('user_task_list'))

            for task in user_task_list:
                finish_times = task.get('finish_times')
                frequency = task.get('frequency') + 1
                task_id = task.get('id')
                member_task_type = task.get('member_task_type')
                if member_task_type == 16 or member_task_type == 13 or member_task_type == 15:
                    continue

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

    def get_task_list(self, task_list):
        if task_list and len(task_list) > 0:
            return task_list
        url = "https://vapp.tmuyun.com/api/user_center/task?type=1&current=1&size=20"

        payload = {}
        headers = self._get_header("/api/user_center/task")
        dict.update(headers, self._get_header2())

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code != 200:
            return []

        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            return resp.get('data').get('list')
        return []

    def get_version(self):
        url = "https://vapp.tmuyun.com/api/app_version/detail"
        payload = {}
        headers = self._get_header("/api/app_version/detail")
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code != 200:
                return

            resp = json.loads(response.content)
            if resp and resp.get('code') == 0:
                self._log("当前app版本：" + str(resp.get('data').get('latest').get('version')))
                TmuYun.app_version = resp.get('data').get('latest').get('version')
        except:
            pass
        finally:
            TmuYun._user_agent = TmuYun.app_version + USER_AGENT_PREFIX
            self._log("user_agent = " + str(TmuYun._user_agent))

    def sign(self):
        self._log("【开始签到】")
        url = "https://vapp.tmuyun.com/api/user_mumber/sign"

        payload = {}
        headers = self._get_header("/api/user_mumber/sign")
        dict.update(headers, self._get_header2())
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            return

        resp = json.loads(response.content)
        if resp and resp.get('code') == 0:
            signExperience = resp.get('data').get('signExperience')
            self._log("签到成功: 获得积分 = " + str(signExperience))
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
        read_time = int(random.random() * 100000)
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

    def invite(self):
        if self.ref_code == TmuYun.ref_core or not self.is_invite:
            return
        random_time(0, 4)
        url = "https://vapp.tmuyun.com/api/account/update_ref_code"

        payload = f'ref_code={TmuYun.ref_core}'
        headers = self._get_header("/api/account/update_ref_code")
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        requests.request("POST", url, headers=headers, data=payload)

    def _get_sign(self, type_id):
        self._timestamp = str(int(time.time() * 1000))
        self._request_id = str(uuid.uuid1())
        self._sign = (
            hashlib.sha256(
                f"{type_id}&&{self.session_id}&&{self._request_id}&&{self._timestamp}&&{SALT}&&{TmuYun.app_id}"
                .encode('utf-8'))
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
            'X-TENANT-ID': str(TmuYun.app_id),
            'User-Agent': self._user_agent,
            'X-ACCOUNT-ID': str(self.account_id),
            'Cache-Control': 'no-cache',
            'Host': 'vapp.tmuyun.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            # 'Cookie': self.cookie
        }

    def _get_header2(self):
        p = ''
        if TmuYun.package_name and TmuYun.package_name != '':
            p = TmuYun.package_name.rsplit(".")[-1]
        return {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": 'Mozilla/5.0 (Linux; Android 13; POCO F2 Pro Build/TQ3A.230705.001; wv) AppleWebKit/537.36 '
                          '(KHTML,like Gecko) Version/4.0 Chrome/115.0.5790.136 Mobile '
                          f'Safari/537.36;xsb_{p};xsb_{p};{TmuYun.app_version};native_app',
            'X-Requested-With': TmuYun.package_name,
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://vapp.tmuyun.com/webFunction/userCenter?tenantId={TmuYun.app_id}&gaze_control=023&isCompleteSign=-1',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def _log(self, msg):
        print(f"{time.strftime('%H:%M:%S', time.localtime())} 【{self.mobile}】: {msg}")
