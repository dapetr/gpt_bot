import requests
from creds import get_creds
import logging


def speech_to_text(data: bytes):

    iam_token, folder_id = get_creds()

    params = "&".join([
        "topic=general",
        f"folderId={folder_id}",
        "lang=ru-RU"
    ])

    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    response = requests.post(
        f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers,
        data=data
    )

    decoded_data = response.json()

    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")
    else:
        logging.debug(f"При запросе в SpeechKit возникла ошибка ({decoded_data.get("error_code")})")
        return False, "При запросе в SpeechKit возникла ошибка"
