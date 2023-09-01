from env import get_env_list
from minimaotai.base import MaoTai

"""
茅台预约-小程序茅台预约，跑脚本需要实名和绑定手机号
@:param 环境变量: LGKX: username=xxx;token=xxx 多账号使用&隔开
抓包: https://gw.huiqunchina.com域名下请求头中X-access-token的值
cron 0 12 * * *
"""


class Lgkx(MaoTai):

    def __init__(self, username, token):
        super().__init__("wx613ba8ea6a002aa8", "乐港空巷", username, token)


def run():
    account_list = get_env_list("LGKX")

    for account in account_list:
        username = account.get("username")
        token = account.get("token")
        Lgkx(username, token).run()


if __name__ == "__main__":
    run()
