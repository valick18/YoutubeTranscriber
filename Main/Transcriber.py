import openai
import properties


class Transcriber:

    openai.api_key = properties.openai_key

    def transcribe(self, path):
        try:
            audio_file = open(path, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript.text
        except Exception as e:
            e.with_traceback()
            return '400'