import json
import requests
from flask import current_app
import time
# def translate(text, source_language, dest_language):
#     """文本翻译"""
#     if 'MS_TRANSLATOR_KEY' not in app.config or \
#             not app.config['MS_TRANSLATOR_KEY']:
#         return _('Error: the translation service is not configured.')
#     auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
#     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
#                      '/Translate?text={}&from={}&to={}'.format(
#                          text, source_language, dest_language),
#                      headers=auth)
#     if r.status_code != 200:
#         return _('Error: the translation service failed.')
#     return json.loads(r.content.decode('utf-8-sig'))
def translate():
    """文本翻译"""
    time.sleep(5)
    return '我爱中国'
