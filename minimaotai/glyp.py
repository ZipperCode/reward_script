from _env import get_env_list
from minimaotai.base import MaoTai

"""
贵旅优品
@:param 环境变量: GLYP: username=xxx;token=xxx 多账号使用&隔开
抓包: https://gw.huiqunchina.com域名下请求头中X-access-token的值
cron: 0 12 * * *
new Env('遵航出山');
"""


class Glyp(MaoTai):

    def __init__(self, username, token):
        super().__init__("wx61549642d715f361", "贵旅优品", username, token)


def run():
    account_list = get_env_list("GLYP")

    for account in account_list:
        username = account.get("username")
        token = account.get("token")
        Glyp(username, token).run()


if __name__ == "__main__":
    run()
