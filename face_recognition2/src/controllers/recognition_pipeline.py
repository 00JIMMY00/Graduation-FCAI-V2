from .recognition_controller import RecognitionController
import json

async def run_recognition_pipeline(rc: RecognitionController):
    await rc.start_recognition()
    result = await rc.get_recognition_result()
    print (json.loads(result))
    return json.loads(result)