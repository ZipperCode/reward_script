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
    return str(hmac.new(sk.encode(), body.encode()), "utf-8")


GMT = "%a, %b %d %Y %H:%M:%S GMT"

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
        "X-HMAC-DIGEST": digest,
        "X-HMAC-Date": t
    }


class MaoTai:
    headers = {
        "content-type": "application/json",
        "Referer": "https://hqmall.huiqunchina.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode":
            "cors",
        "Sec-Fetch-Site":
            "cross-site",
        "xweb_xhr":
            "1",
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 "
            "Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows "
            "WindowsWechat/WMPF XWEB/6945",
    }

    host = "https://gw.huiqunchina.com"

    def __init__(self, app_id, token):
        self.app_id = app_id
        self.token = token
        self.ak = ""
        self.sk = ""
        self.between_time = 0
        self.channel = ""
        self.headers = {}
        self.has_error = False

        self._status = 0
        self._phone_is_bind = False
        self._is_real_name_auth = False

        self.token_dict = {
            "Channel": "miniapp",
            "DataType": "json",
            "X-access-:ken": self.token,
        }

    def init(self):
        body = f"""{"appId":"{self.app_id}"}"""
        response = requests.post("https://callback.huiqunchina.com/api/getInfo", json=body)
        if response.status_code != 200:
            self.has_error = True
            return
        resp = json.loads(response.text)
        if resp and resp.get("code") == "10000":
            data = resp.get("data")
            self.ak = data.get("ak")
            self.sk = data.get('sk')

    def _enable(self):
        return not self.has_error and not self.ak and not self.sk and len(self.ak) > 0 and len(self.sk) > 0

    def get_channel(self):
        if not self._enable():
            return
        url = "/front-manager/api/get/channelId"
        body = f"""{"appId":"{self.app_id}"}"""
        resp = self._post(url, body)
        if len(resp) > 0:
            self.channel = str(resp.get("data", 5))

    def check_login(self):
        if not self._enable():
            return None

        url = "/front-manager/api/customer/queryById/token"
        body = """{"channel":"h5"}"""
        resp = self._post(url, body)

        if len(resp) > 0 and resp.get("code") == "10000":
            data = resp.get("data")
            if data is dict and len(data) > 0:
                self._status = data.get("status")
                self._is_real_name_auth = data.get("isRealNameAuth")
                self._phone_is_bind = data.get("phoneIsBind")
            pass

        return len(resp) > 0

    def channel_activity(self):
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

        text = f"""
活动编号        = {act_id}
活动名称        = {name}
是否预约        = {"是" if (is_appoint == 1) else "否"}
服务时间        = {to_fmt(sys_current_time)}
活动时间        = {to_fmt(start_time)} ~ {to_fmt(end_time)}
预约人数        = {appoint_counts}
预约时间        = {to_fmt(appoint_start_time)} ~ {to_fmt(appoint_end_time)}
开奖时间        = {to_fmt(draw_time)}
下单时间        = {to_fmt(purchase_start_time)} ~ {to_fmt(purchase_end_time)}
        """
        MaoTai.log(text)
        return act_id

    def _check_consumer(self, activity_id):
        url = "/front-manager/api/customer/promotion/checkCustomerInQianggou"
        body = f"""\\{"activityId":{activity_id},"channelId":{self.channel}\\}"""
        resp = self._post(url, body)
        if resp.get("code") != "10000":
            return False
        MaoTai.log(str(resp))
        return True

    def appoint(self, activity_id):
        if self._check_consumer(activity_id):
            return
        url = "/front-manager/api/customer/promotion/appoint"
        body = f"""\\{"activityId":{activity_id},"channelId":{self.channel}\\}"""
        resp = self._post(url, body)
        MaoTai.log(str(resp))

    def _post(self, url: str, body: str) -> dict:
        headers = {}
        h = encrypt("POST", url, body, self.between_time, self.ak, self.sk)
        dict.update(headers, MaoTai.headers)
        dict.update(headers, self.token_dict)
        dict.update(headers, h)
        response = requests.post(MaoTai.host + url, json=body, headers=headers)
        if response.status_code != 200:
            self.has_error = True
            return {}
        resp = json.loads(response.text)
        if resp and resp.get('code') == "10000":
            s_time = resp.get("serverTimeStamp")
            c_time = int(time.time() * 1000)
            self.between_time = s_time - c_time
        return resp

    @classmethod
    def log(cls, msg):
        print(msg)


if __name__ == "__main__":
    # Thu, 31 Aug 2023 13:59:48 GMT
    print()
