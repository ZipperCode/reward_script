import os
from typing import List


def get_env_list(key: str) -> List[dict]:
    """
    环境变量列表 key1=value1;key2=value2&key1=value1;key2=value2
    :param key: key
    :return:
    """
    env_values = os.environ.get(key)
    if not env_values:
        return []

    env_values = str(env_values).split("&")
    if len(env_values) < 0:
        return []

    result = []
    for env_value in env_values:
        p_values = env_value.split(";")
        _dict = {}

        for param in p_values:
            kv = param.split("=")
            if not kv or len(kv) < 2:
                continue
            k, v = kv
            _dict[k] = v

        if len(_dict) > 0:
            result.append(_dict)

    return result
