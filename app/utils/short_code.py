# ============================================================
# 短码生成工具
# 作用：生成随机的短码，用于短链接的唯一标识
# ============================================================

import string
import random


def generate_short_code(length: int = 6) -> str:
    """
    生成指定长度的随机短码

    字符集：a-z + A-Z + 0-9，共 62 个字符
    6 位长度的组合数：62^6 = 568 亿种，基本不会重复

    举例：aB3xK9、mN7pQ2、Rt5yW8
    """
    chars = string.ascii_letters + string.digits  # 62个字符
    return ''.join(random.choices(chars, k=length))
