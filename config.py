HOME_DIR = '/home/student/gpt_bot'

BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'

MAX_USERS = 3
MAX_GPT_TOKENS = 120
COUNT_LAST_MSG = 4

MAX_USER_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5_000
MAX_USER_GPT_TOKENS = 2_000

LOGS = 'logs.txt'
DB_FILE = f'{HOME_DIR}/database.db'

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]
