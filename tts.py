import requests
from creds import get_creds
import logging


IAM_TOKEN, folder_id = get_creds()


def text_to_speech(text):
    headers = {'Authorization': f'Bearer {IAM_TOKEN}'}
    data = {'text': text,
            'lang': 'ru-RU',
            'voice': 'marina',
            'emotion': 'friendly',
            'folderId': folder_id, }

    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return True, response.content
    else:
        logging.debug(f"При запросе в SpeechKit возникла ошибка ({response.status_code})")
        return False, "При запросе в SpeechKit возникла ошибка"
