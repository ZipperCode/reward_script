import json
import os
import random
import time

import requests

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'xjsp')

HOST = "tkqq27ce5bwb.litbir.com"

HOST_NAME = 'https://' + HOST

HEADERS = [
    {
        'Cookie': '',
        'Cache-Control': 'public,max-age:0',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'okhttp/3.11.0',
        'Content-Type': 'multipart/form-data'
    }
]

app_version = "4.1.7"


def get_version():
    url = "https://i3eelm2qo4vw.f5q635.com/init"
    payload = {}
    headers = {
        'user-agent': 'Dart/2.19 (dart:io)'
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            resp = json.loads(response.content)
            if resp.get('retcode') == 0:
                g_data = resp.get('data').get('globalData')
                global app_version
                app_version = g_data.get('appver').get('AndroidVer')
    except:
        pass


get_version()


def _get_common_body():
    return {
        "pid": "",
        "apiVersion": "30",
        "deviceModel": "Redmi%20K20%20Pro",
        "brand": "Xiaomi",
        "deviceName": "raphael",
        "serial": "unknown",
        "platform": "android",
        "version": app_version,
        "_t": str(int(time.time()))
    }


CONTENTS = [
    "舒服", "好喜欢", "爽", "身体不行了"
]


class Xjsp:

    def __init__(self, phone: str = None, password: str = None, token: str = None):
        self.phone = phone
        self.password = password
        self.token = token
        self.xxx_api_auth = "xxx_api_auth="
        self.headers = list.copy(HEADERS)
        self.user = {}

    def run(self):

        pass

    def index(self):
        self._log("开始 查询用户金币")
        url = HOST_NAME + "/ucp/index"
        body = _get_common_body()
        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("index#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') != 0:
            self._log("index#msg = " + str(resp.get('errmsg')))
            return

        data = resp.get('data')
        if not isinstance(data, dict):
            self._log("index#not isinstance(data, dict)")
            return

        self.user = data.get('user')
        if data.get('user') and data.get('user').get('mobi'):
            self._log(f"查询金币: 成功 🎉数量为:{data.get('user').get('user').get('goldcoin')}")
            return
        self._log("index#获取用户信息失败")

    def sign(self):
        url = HOST_NAME + "/ucp/task/sign"
        body = _get_common_body()
        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("sign#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') != 0:
            self._log("签到失败: " + str(resp.get('errmsg')))
        else:
            self._log("签到成功: " + str(resp.get("errmsg")))

    def _task_box(self, task_id):
        url = "https://3uajypt1fyfe.xzjgz.com/ucp/taskbox/taskboxopen"
        body = _get_common_body()
        body['taskid'] = task_id

        response = requests.post(url, data=body, headers=self.headers[0])

        self._log("task_box#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log(f"开宝箱{task_id}成功，获得金币：" + str(resp.get('data').get("taskdone")))
        else:
            self._log(f"开宝箱{task_id}失败, " + str(resp.get("errmsg")))

    def box(self):
        self._task_box(1022)
        self._task_box(1622)

    def qr_save(self):
        url = "/ucp/task/qrcodeSave"
        body = _get_common_body()
        response = requests.post(url, data=body, headers=self.headers[0])

        self._log("task_box#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log("保存二维码图片任务: 成功 🎉：" + str(resp.get('errmsg')))
        else:
            self._log("保存二维码图片任务: 失败" + str(resp.get('errmsg')))

    def video_task(self):
        self._log("开始视频相关任务")
        r = random.randint(0, 0xd6d8)
        url = HOST_NAME + "/vod/reqplay/" + str(r)
        body = _get_common_body()
        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("视频任务#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log("视频任务: 成功 🎉：" + str(resp.get('errmsg')))
        else:
            self._log("视频任务: 失败" + str(resp.get('errmsg')))

    def ad_view_click(self):
        url = HOST_NAME + "/ucp/task/adviewClick"
        body = _get_common_body()
        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("点击广告任务#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log("点击广告任务: 成功 🎉 " + str(resp.get('errmsg')))
        else:
            self._log("点击广告任务: 失败 " + str(resp.get('errmsg')))

    def common_post(self, vo_did):
        url = HOST_NAME + "/comment/post"
        body = _get_common_body()
        body['vodid'] = vo_did
        body['parentid'] = 0
        body['content'] = random.choice(CONTENTS)
        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("评论任务#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log("评论任务: 成功 🎉 " + str(resp.get('errmsg')))
        else:
            self._log("评论任务: 失败 " + str(resp.get('errmsg')))

    def add_fav(self, vo_did):
        url = HOST_NAME + "/favorite/add"
        body = _get_common_body()
        body['vodid'] = vo_did + "_"
        body['parentid'] = 0

        response = requests.post(url, data=body, headers=self.headers[0])
        self._log("添加喜欢#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') == 0:
            self._log("添加喜欢任务: 成功 🎉 " + str(resp.get('errmsg')))
        else:
            self._log("添加喜欢任务: 失败 " + str(resp.get('errmsg')))

    def login(self):
        url = 'https://hsb5ipyxhh6c.duiquanzhekou.com/login'
        body = _get_common_body()
        body['mobi'] = self.phone
        body['password'] = self.password
        h = {
            "Content-Type": "application/x-www-form-urlencode"
        }
        response = requests.post(url, data=body, headers=h)
        self._log("login#resp = " + str(response.status_code) + ":" + str(response.text))
        if response.status_code != 200:
            return
        resp = json.loads(response.content)
        if resp.get('retcode') != 0:
            self._log("login#msg = " + str(resp.get('errmsg')))
            return

        data = resp.get('data')
        if not isinstance(data, dict):
            self._log("login#not isinstance(data, dict)")
            return
        xxx_api_auth = data.get('xxx_api_auth')

        self.xxx_api_auth = xxx_api_auth
        self._on_login(xxx_api_auth)
        for header in self.headers:
            dict.update(header, {"Cookie": "xxx_api_auth=" + self.xxx_api_auth})

    def _on_login(self, token):
        self.token = token
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        with open(os.path.join(DATA_DIR, self.phone + ".json"), "w") as f:
            f.write(token)

    def _read_token(self):
        p = os.path.exists(os.path.join(DATA_DIR, self.phone + ".json"))
        if not p:
            return None
        with open(p, 'r') as f:
            self.token = f.read().strip()

        return self.token

    def _log(self, msg):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} : {msg}")


if __name__ == "__main__":
    Xjsp().run()
