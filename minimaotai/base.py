import base64
import datetime
import hmac
import json
import time

import requests


def signature(method: str, url: str, ak: str, sk: str, date_time: str) -> str:
    """
    X-HMAC-SIGNATURE
    """
    text = method + "\n" + url + "\n\n" + ak + "\n" + date_time + "\n"
    _hmac = hmac.new(sk.encode(), text.encode(), "sha256")
    return base64.b64encode(_hmac.digest()).decode()


def digest(body: str, sk: str) -> str:
    return str(base64.b64encode(hmac.new(sk.encode(), body.encode(), "sha256").digest()).decode())


GMT = "%a, %d %b %Y %H:%M:%S GMT"

FMT = "%Y-%m-%d %H:%M:%S"


def to_fmt(t: int) -> str:
    return time.strftime(FMT, time.localtime(t / 1000))


def encrypt(method: str, url: str, body: str, between_time: int, ak: str, sk: str) -> dict:
    t = int(time.time() * 1000) + between_time
    t = datetime.datetime.utcfromtimestamp(t / 1000).strftime(GMT)
    _signature = signature(method, url, ak, sk, t)
    _digest = digest(body, sk)

    return {
        "X-HMAC-SIGNATURE": _signature,
        "X-HMAC-ACCESS-KEY": ak,
        "X-HMAC-ALGORITHM": "hmac-sha256",
        "X-HMAC-DIGEST": _digest,
        "X-HMAC-Date": t
    }


class MaoTai:
    _headers = {
        "content-type": "application/json",
        "Referer": "https://hqmall.huiqunchina.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "xweb_xhr": "1",
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 "
            "Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows "
            "WindowsWechat/WMPF XWEB/6945",
    }

    host = "https://gw.huiqunchina.com"

    def __init__(self, app_id, app_name, username, token):
        self.app_id = app_id
        self.app_name = app_name
        self.username = username
        self.token = token
        self._ak = ""
        self._sk = ""
        self._between_time = 0
        self._channel = ""
        self._headers = {}
        self._has_error = False

        self._status = 0
        self._phone_is_bind = False
        self._is_real_name_auth = False

        self._token_dict = {
            "Channel": "miniapp",
            "DataType": "json",
            "X-access-token": self.token,
        }

        self._act_id = 0
        self._act_name = ""
        self._act_start = 0
        self._act_end = 0
        self._act_appoint_start = 0
        self._act_appoint_end = 0
        self._act_draw = 0
        self._purchase_start = 0
        self._purchase_end = 0
        self._act_appoint_count = 0
        self._act_is_appoint = False

    def init(self):
        body = {
            "appId": self.app_id
        }
        response = requests.post("https://callback.huiqunchina.com/api/getInfo", json=body)
        if response.status_code != 200:
            self._has_error = True
            return
        resp = json.loads(response.content)
        self.log("resp = " + str(resp))
        if resp and resp.get("code") == "10000":
            data = resp.get("data")
            self._ak = data.get("ak")
            self._sk = data.get('sk')

    def _enable(self):
        return not self._has_error and self._ak and self._sk and len(self._ak) > 0 and len(self._sk) > 0

    def get_channel(self):
        if not self._enable():
            return
        url = "/front-manager/api/get/channelId"
        body = {
            "appId": self.app_id
        }
        body = json.dumps(body)
        resp = self._post(url, body)
        if len(resp) > 0:
            self._channel = str(resp.get("data", 5))
        else:
            self._has_error = True

    def check_login(self):
        if not self._enable():
            return None

        url = "/front-manager/api/customer/queryById/token"
        body = {
            "channel": "h5"
        }
        body = json.dumps(body)
        resp = self._post(url, body)
        success = len(resp) > 0 and resp.get("code") == "10000"
        if success:
            data = resp.get("data")
            if data is dict and len(data) > 0:
                self._status = data.get("status")
                self._is_real_name_auth = data.get("isRealNameAuth", False)
                self._phone_is_bind = data.get("phoneIsBind", False)
                self.log(f"账号状态: {'可用' if self._status == 1 else '不可用'}")
                self.log(f"是否实名: {'已实名' if self._is_real_name_auth else '未实名'}")
                self.log(f"是否绑定手机: {'已绑定' if self._phone_is_bind else '未绑定'}")

        return success

    def channel_activity(self):
        if not self._enable():
            return None
        url = "/front-manager/api/customer/promotion/channelActivity"
        body = "{}"
        resp = self._post(url, body)
        if resp.get("code") != "10000":
            return None
        data = resp.get("data")
        if not data or data is not dict:
            return None
        name = data.get("name")
        act_id = data.get("id", 0)
        start_time = data.get("startTime", 0)
        end_time = data.get("endTime", 0)
        sys_current_time = data.get("sysCurrentTime", 0)
        appoint_start_time = data.get("appointStartTime", 0)
        appoint_end_time = data.get("appointEndTime", 0)
        draw_time = data.get("drawTime", 0)
        purchase_start_time = data.get("purchaseStartTime", 0)
        purchase_end_time = data.get("purchaseEndTime", 0)
        appoint_counts = data.get("appointCounts", 0)
        is_appoint = data.get("isAppoint", 0)

        self._act_id = act_id
        self._act_name = name
        self._act_start = start_time
        self._act_end = end_time
        self._act_appoint_start = appoint_start_time
        self._act_appoint_end = appoint_end_time
        self._act_draw = draw_time
        self._purchase_start = purchase_start_time
        self._purchase_end = purchase_end_time
        self._act_appoint_count = appoint_counts
        self._act_is_appoint = True if is_appoint == 1 else False

        text = f"""
活动编号        = {act_id}
活动名称        = {name}
是否预约        = {"是" if (is_appoint == 1) else "否"}
服务时间        = {to_fmt(sys_current_time)}
本地时间        = {to_fmt(time.time_ns())}
活动时间        = {to_fmt(start_time)} ~ {to_fmt(end_time)}
预约人数        = {appoint_counts}
预约时间        = {to_fmt(appoint_start_time)} ~ {to_fmt(appoint_end_time)}
开奖时间        = {to_fmt(draw_time)}
下单时间        = {to_fmt(purchase_start_time)} ~ {to_fmt(purchase_end_time)}
        """
        self.log(text)
        return data

    def _check_consumer(self, activity_id):
        url = "/front-manager/api/customer/promotion/checkCustomerInQianggou"
        body = {
            "activityId": activity_id,
            "channelId": self._channel
        }
        body = json.dumps(body)
        resp = self._post(url, body)
        if resp.get("code") != "10000":
            return False
        self.log(str(resp))
        return True

    def appoint(self, activity_id):
        if not self._enable():
            return
        if self._check_consumer(activity_id):
            return
        url = "/front-manager/api/customer/promotion/appoint"
        body = {
            "activityId": activity_id,
            "channelId": self._channel
        }
        body = json.dumps(body)
        resp = self._post(url, body)
        self.log(str(resp))

    def _post(self, url: str, body: str) -> dict:
        headers = {}
        h = encrypt("POST", url, body, self._between_time, self._ak, self._sk)
        dict.update(headers, MaoTai._headers)
        dict.update(headers, self._token_dict)
        dict.update(headers, h)
        dict.update(headers, {'Content-Type': 'application/json; charset=UTF-8'})
        response = requests.post(MaoTai.host + url, data=body, headers=headers)
        if response.status_code != 200:
            print("resp = " + response.text)
            self._has_error = True
            return {}
        resp = json.loads(response.text)
        if resp and resp.get('code') == "10000":
            s_time = resp.get("serverTimeStamp")
            c_time = int(time.time() * 1000)
            self._between_time = s_time - c_time
        print("resp = " + str(resp))
        return resp

    def run(self):
        self.init()
        if not self._enable():
            self.log("初始化失败")
            return
        self.get_channel()
        is_login = self.check_login()
        if not is_login:
            self.log("token失效，请重新获取")
            self._send_msg("token失效，请重新获取")
            return

        if not self._is_real_name_auth:
            self.log("账号未实名，请先处理实名")
            self._send_msg("账号未实名，请先处理实名")
            return
        if not self._phone_is_bind:
            self.log("账号未绑定手机，请先绑定手机")
            self._send_msg("账号未绑定手机，请先绑定手机")
            return
        self.channel_activity()

    def log(self, msg):
        print(f"{to_fmt(int(time.time() * 1000))}:【{self.app_name}-{self.username}】" + msg)

    def _send_msg(self, msg):
        try:
            from sendNotify import send
            send(f"{self.app_name}-{self.username}", msg)
        except Exception as e:
            print(e)
            print(f"通知失败，通知模块不存在: {msg}")


if __name__ == "__main__":
    # Thu, 31 Aug 2023 13:59:48 GMT
    print(encrypt("POST", "/front-manager/api/customer/queryById/token", {
        "channel": "h5"
    }, 0, "39414a3d423249ffb2fec95915fd9ac6", "634143d4f5b08349fa83d92366e19fc1"))
    print()
