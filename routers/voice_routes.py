from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi import UploadFile, File
from voice2txt.src.Controllers import SpeechController
from .pathEnums import PathEnums

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def voice_text_page():
    """Serve the HTML page for voice recognition."""
    with open(PathEnums.voicetemplate.value, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.get("/start")
async def start_recording():
    """Process voice input directly from microphone."""
    controller = SpeechController()
    result = await controller.process_speech()
    return result

@router.get("/result")
async def get_recording_result():
    """Fetch the recognition result without starting the process."""
    result = await start_recording().result
    return {"status": "fetched", "result": result}