#encoding=utf-8
import json
import os
os.environ['PYTHON_EGG_CACHE']='/data/data/com.termux/files/home/.python-egg'
from PIL import Image
import requests
import base64
from common.log import logger

class OCR:
    access_token = '24.37dc0a0d45bc677243fa5e200d9c42ea.2592000.1583323598.282335-18162419'
    api_key = 'iw70pibFazASK3Ki6IVPbZpi'
    secret_key = 'kPI3lmhlllywPlGPZCMePZDcEsH4CbI2'
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}'

    def __init__(self, raw_pic_path):
        self._pic = Image.open(raw_pic_path)

    def crop(self, left, top, right, buttom):
        self._pic = self._pic.crop((left, top, right, buttom))

    def binaryzation(self, threshold=113):
        self._pic = self._pic.convert('RGB')
        width, height = self._pic.size
        im = Image.new("RGB", (width, height))
        for i in range(width):
            for j in range(height):
                r, g, b = self._pic.getpixel((i, j))
                pix = (r + g + b) / 3
                if pix >= threshold:
                    r, g, b = 255, 255, 255
                im.putpixel((i, j), (r, g, b))  # （i,j）为坐标，后面的是像素点
        self._pic = im

    def save(self, path):
        self._pic.save(path)

    def get_text(self, path):
        data = {'image': base64.b64encode(open(path, 'rb').read()).decode(),
                'language_type': 'ENG', 'probability': 'true'}
        while True:
            params = {'access_token': OCR.access_token,
                      'aipSdk': 'python', 'aipVersion': '2_2_18'}
            try:
                r = requests.post('https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic', data=data, params=params,
                                  headers={}, verify=False)
                r.raise_for_status()
            except BaseException as e:
                logger.error(f'ocr请求失败, {e}')
                return ''
            try:
                ret = json.loads(r.content.decode('utf8'))
            except BaseException as e:
                logger.error(f"json不正确: {r.content.decode('utf8')}")
                return ''
            logger.info(ret)
            if ret.get('error_code', 0) == 111:
                response = requests.get(OCR.host)
                if response:
                    OCR.access_token = response.json()['access_token']
                    logger.info('access_token 过期，已重新获取')
                    continue
                else:
                    logger.error(f'access_token 更新失败')
                    return ''
            words_reuslt = list(map(lambda x: (x['words'], x['probability']['average']), ret['words_result']))
            words_reuslt.sort(key=lambda x:x[1], reverse=True)
            return words_reuslt[0][0]

if __name__ == '__main__':
    # encoding:utf-8
    import requests

    try:
        a = json.dumps({'taskId': 1, 'status': 0})
        r = requests.get(url='http://atf.wuwotech.com/api/ele/kcard?taskId=1&status=0')
        r.raise_for_status()
        t = r.content
    except BaseException as e:
        logger.warning(f'发送k宝状态失败 taskid:{taskid} status: {status}')


    api_key = 'iw70pibFazASK3Ki6IVPbZpi'
    api_key = 'hWrM6iNlMuf4O4feXeugxFD0'
    secret_key = 'kPI3lmhlllywPlGPZCMePZDcEsH4CbI2'
    secret_key = 'kb86zSGt4YGLwmCTnZikrG6IFDeiIS0e'
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}'
    response = requests.get(host)
    if response:
        print(response.json()['access_token'])


