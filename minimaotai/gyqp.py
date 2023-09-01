from env import get_env_list
from minimaotai.base import MaoTai

"""
贵盐黔品-小程序茅台预约，跑脚本需要实名和绑定手机号
@:param 环境变量: GYQP: username=xxx;token=xxx 多账号使用&隔开
抓包: https://gw.huiqunchina.com域名下请求头中X-access-token的值
cron 0 12 * * *
"""


class Gyqp(MaoTai):

    def __init__(self, username, token):
        super().__init__("wx5508e31ffe9366b8", "贵盐黔品", username, token)


def run():
    account_list = get_env_list("GYQP")

    for account in account_list:
        username = account.get("username")
        token = account.get("token")
        Gyqp(username, token).run()


if __name__ == "__main__":
    run()