import os
import wave
from typing import Literal
from string import Template
import json
import requests
import datetime
import logging

import tts.soundControl as sc
import tts.params as params

logger = logging.getLogger("main.tts")

class TTSAudio :
    def __init__(
            self,
            cache_path : str,
            is_stream : bool = True,
            is_play : bool = False,
            request_url : str = params.DEFAULT_REQUEST_FULL_URL,
            tts_endpoint : str = params.DEFAULT_TTS_ENDPOINT,
            character_endpoint : str = params.DEFAULT_CHARACTER_ENDPOINT,
            character : str = params.DEFAULT_CHARACTER_NAME,
            text_language : Literal["中文","英文","日文","中英混合","日英混合","多语种混合"] = "多语种混合",
            emotion : str = params.DEFAULT_EMOTION,
            ) -> None:
        # wav file folder
        self.cache_path = cache_path

        # api
        self.tts_url = request_url + tts_endpoint
        self.character_url = request_url + character_endpoint

        # TTS settings
        self.text_language = text_language
        self.character = character
        self.emotion = emotion

        if is_stream is True and is_play is False:
            logger.warning("is_play is ignored (always True) when is_stream is True")

        self.is_stream = is_stream
        self.is_play = is_play

        if is_stream is True:
            self.audio = sc.responseStreamAudio()
        else:
            self.audio = sc.Audio()

    def tts_request(
        self,
        text : str,
        text_language : Literal["中文","英文","日文","中英混合","日英混合","多语种混合"] = None,
        emotion : str = None,
        ):
        if emotion is None :
            emotion = self.emotion
        if text_language is not None:
            self.text_language = text_language
        logger.info(f"send tts request. language:{self.text_language} emotion:{emotion} content:{text}")

        #print(text)
        unencode_text = requests.utils.quote(text)

        endpoint_template = Template(params.DEFAULT_ENDPOINT_DATA)
        filled_endpoint_data = endpoint_template.substitute(
            chaName = self.character,
            characterEmotion = self.emotion,
            speakText = unencode_text,
            textLanguage = self.text_language,
            stream = self.is_stream,
        )

        request_data = json.loads(filled_endpoint_data)
        body = request_data["body"]
        
        response = requests.post(
            self.tts_url,
            json=body,
            stream=self.is_stream)

        if response.status_code == 200 :
            logger.info("Successfully get response. code:200")
            if self.is_stream is True :
                self.audio.play_stream(response)
                while self.audio.thread.is_alive():
                    yield self.audio.start_speak
            else :
                file_path = os.path.join(self.cache_path,self.get_cache_file_name)
                with wave.open(file_path, 'wb') as wf:
                    wf.writeframes(response.content)
                logger.debug(f"A wav file was saved at {file_path}")
                if self.is_play is True :
                    self.audio.play_wav_file(file_path)
                return file_path
        else:
            logger.error(f"Failed to get response. code:{response.status_code} content:{response.content}")


    @staticmethod
    def get_cache_file_name() -> str :
        """生成格式为'%Y%m%d%H%M%S%f'的文件名
        Returns :
            str : 生成的文件名
        """
        return f"/{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav"

    def stop_play(self):
        self.audio.stop()

    def get_tts_character(self) :
        response = requests.get(url=self.character_url)
        character_list = json.loads(response.content)
        return character_list

    def set_tts_character(self, character : str) :
        self.character = character
