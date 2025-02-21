from fastapi import APIRouter
from fastapi.responses import HTMLResponse
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
    """Start the voice recognition process and return a result."""
    result = SpeechController().process_speech()
    return {"status": "completed", "result": result}

@router.get("/result")
async def get_recording_result():
    """Fetch the recognition result without starting the process."""
    result = await start_recording().result
    return {"status": "fetched", "result": result}