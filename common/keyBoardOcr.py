# -*- coding:UTF-8 -*-
# -*- encoding: utf-8 -*-
import base64
import requests
from urllib.parse import quote
import json

class KeyBoardOcr:
    recognise_api_url = "https://aip.baidubce.com/rest/2.0/solution/v1/iocr/recognise"
    headers = {'Content-Type': "application/x-www-form-urlencoded", 'charset': "utf-8"}
    access_token = "24.8b4e7fa4a0b75925b29c2cc49b4faa0f.2592000.1585834179.282335-18613576"
    templateSign = "78ca7d7b1c20f85bedacf65f61ddbc99"

    @staticmethod
    def Ocr(pic_path, templateSign):
        try:
            with open(pic_path, 'rb') as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode().replace("\r", "")

            # 请求模板的bodys
            recognise_bodys = "access_token=" + KeyBoardOcr.access_token + "&templateSign=" + templateSign + \
                              "&image=" + quote(image_b64.encode("utf8"))
            # 请求模板识别
            response = requests.post(KeyBoardOcr.recognise_api_url, data=recognise_bodys, headers=KeyBoardOcr.headers)
            # 请求分类器识别
            # response = requests.post(recognise_api_url, data=classifier_bodys, headers=headers)
            res = json.loads(response.text)
            res = {key['word']: key['word_name'] for key in res['data']['ret']}
            return res
        except BaseException as e:
            return dict()
