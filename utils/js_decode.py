# -*- coding: UTF-8 -*-
import codecs
import re

import execjs

if __name__ == "__main__":

    # with codecs.open("./test.js", 'r', encoding='gb18030') as f:
    #     js_text = f.read()
    #     js_text = re.sub('[\u4e00-\u9fa5]', '', js_text)
    #     text_lines = js_text.splitlines()
    #
    # ctx = execjs.compile(js_text)
    #
    # pattern = r'_0x322a03\(0x[\da-fA-F]+,\s*\'[^\']+\'\)'
    # with open("./test_decode.js", 'w', encoding='utf-8') as f:
    #     for l in text_lines:
    #         matches = re.findall(pattern, l)
    #         # 打印匹配结果
    #         for match in matches:
    #             print("match = " + match)
    #             result = ctx.call(match)
    #             l = l.replace(match, result)
    #
    #         f.write(l)
    # 读取 JavaScript 文件
    with open('./test.js', 'r', encoding='utf-8') as f:
        js_code = f.read()

    pattern = r'(var\s+)(\w+)\s+=\s+_0x322a03[,;]([\s\S]*?)([,;])'
    replacement = r'\1_0x322a03 = _0x322a03\3'
    js_code = re.sub(pattern, replacement, js_code)

    pattern = r'(var\s+)(\w+)\s+=\s+_0x37c16c[,;]([\s\S]*?)([,;])'
    replacement = r'\1_0x37c16c = _0x37c16c\3'
    js_code = re.sub(pattern, replacement, js_code)

    # 使用正则表达式替换匹配的行代码
    pattern = r'(var\s+)(\w+)\s+=\s+_0x2846[,;]([\s\S]*?)([,;])'
    replacement = r'\1_0x2846 = _0x2846\3'
    js_code = re.sub(pattern, replacement, js_code)

    # 将替换后的 JavaScript 代码写回文件
    with open('./test_1.js', 'w', encoding='utf-8') as f:
        f.write(js_code)

