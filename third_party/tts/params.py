DEFAULT_REQUEST_URL = r"http://127.0.0.1"
DEFAULT_REQUEST_PORT = 5000
DEFAULT_REQUEST_FULL_URL = f"{DEFAULT_REQUEST_URL}:{DEFAULT_REQUEST_PORT}"
DEFAULT_TTS_ENDPOINT = r"/tts"
DEFAULT_CHARACTER_ENDPOINT = r"/character_list"

DEFAULT_CHARACTER_NAME = "晴"
DEFAULT_EMOTION = "default"

DEFAULT_ENDPOINT_DATA = """{
    "method": "POST",
    "body": {
        "cha_name": "${chaName}",
        "character_emotion": "${characterEmotion}",
        "text": "${speakText}",
        "text_language": "${textLanguage}",
        "stream": "${stream}",
        "save_temp": "False"
    }
}"""
