from env import get_env_list
from minimaotai.base import MaoTai

"""
遵航出山-小程序茅台预约，跑脚本需要实名和绑定手机号
@:param 环境变量: ZHCS: username=xxx;token=xxx 多账号使用&隔开
抓包: https://gw.huiqunchina.com域名下请求头中X-access-token的值
cron 0 12 * * *
"""


class Zhcs(MaoTai):

    def __init__(self, username, token):
        super().__init__("wx624149b74233c99a", "遵航出山", username, token)


def run():
    account_list = get_env_list("ZHCS")

    for account in account_list:
        username = account.get("username")
        token = account.get("token")
        Zhcs(username, token).run()


if __name__ == "__main__":
    run()
