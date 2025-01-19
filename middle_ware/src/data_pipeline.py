import sys
import os
from face_recognition2 import RecognitionController

class DataPipeline:
    def __init__(self):
        pass

    async def start_recognition(self):
        self.recognition_controller = RecognitionController()
        await self.recognition_controller.start_recognition()
        return await self.recognition_controller.get_recognition_result()
