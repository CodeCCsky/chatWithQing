import logging
import os
import threading
import wave

import pyaudio

import tts.soundControl.params as pms

logger = logging.getLogger("main.tts.soundControl")


class Audio:
    def __init__(self, output_device_index: int = None) -> None:
        self.p = pyaudio.PyAudio()
        self.file_path = None
        self.output_device_index = output_device_index

        # Thread
        self.thread: threading.Thread = None
        self.stop_event = threading.Event()

    def play_wav_file(self, wav_path: str) -> None:
        logger.info(f"Load wav file at {wav_path}")
        if os.path.exists(wav_path) is False:
            logger.error(f"{wav_path} not exists")
            raise FileNotFoundError("wav file not exists")

        # Stop the playing Audio, if any
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

        # Reset
        self.stop_event.clear()
        self.file_path = wav_path

        # Create new thread
        self.thread = threading.Thread(target=self._play_thread)
        self.thread.start()

    def _play_thread(self) -> None:
        try:
            wf = wave.open(self.file_path, "rb")
            logger.debug(
                f"{self.file_path} start playing. \
sampwidth:{wf.getsampwidth()} channels:{wf.getnchannels()} framerate:{wf.getframerate()}"
            )
            stream = self.p.open(
                format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output_device_index=self.output_device_index,
                output=True,
            )
            data = wf.readframes(1024)
            while data and not self.stop_event.is_set():
                stream.write(data)
                data = wf.readframes(1024)

            wf.close()
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(e)
            raise e

    def stop(self) -> None:
        logger.debug("Stop signal set")
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def __del__(self) -> None:
        self.p.terminate()
        self.stop()


import audioop

from requests import Response


class responseStreamAudio:
    def __init__(self, output_device_index: int = None) -> None:
        self.output_device_index = output_device_index
        self.wav_generator = None
        self.rate = None
        self.channels = None
        self.width_format = None
        self.start_speak = False
        self.p = pyaudio.PyAudio()

        # Thread
        self.thread: threading.Thread = None
        self.stop_event = threading.Event()

    def play_stream(
        self, wav_generator: Response, rate: int = pms.RATE, channels: int = pms.CHANNELS, width_format=pms.WIDTH_FORMAT
    ) -> None:
        logger.info("Load stream wav")

        # Stop the playing Audio, if any
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

        # Reset
        self.stop_event.clear()
        self.wav_generator = wav_generator
        self.rate = rate
        self.channels = channels
        self.width_format = width_format

        # Create new thread
        self.thread = threading.Thread(target=self._play_thread)
        self.thread.start()

    def _play_thread(self) -> None:
        try:
            logger.debug(
                f"start playing stream. \
sampwidth:{self.width_format} channels:{self.channels} framerate:{self.rate}"
            )
            stream = self.p.open(
                format=self.width_format,
                channels=self.channels,
                rate=self.rate,
                output_device_index=self.output_device_index,
                output=True,
            )
            for audio_chunk in self.wav_generator.iter_content(chunk_size=pms.THUNK):
                if self.stop_event.is_set():
                    break
                stream.write(audio_chunk)
                rms = audioop.rms(audio_chunk, 2)
                if rms > 100 and rms < 10000:
                    self.start_speak = True

            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(e)
            raise e

    def get_speak_state(self) -> bool:
        return self.start_speak

    def stop(self) -> None:
        logger.debug("Stop signal set")
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def __del__(self) -> None:
        self.p.terminate()
        self.stop()
