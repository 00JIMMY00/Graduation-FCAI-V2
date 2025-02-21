from ..Services.SpeechService import SpeechService
import json


class SpeechController:
    def __init__(self):
        self.service = SpeechService()

    async def process_speech(self, audio_file_path=None):
        """Process speech from microphone or audio file."""
        if audio_file_path:
            result = await self.service.audio_file_to_text(audio_file_path)
        else:
            result = await self.service.voice_to_text()
        return result