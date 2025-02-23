from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from face_recognition2 import RecognitionController
from .pathEnums import PathEnums

router = APIRouter()
rc = RecognitionController()

@router.get("/", response_class=HTMLResponse)
async def face_recognition_page():
    """Serve the HTML page for face recognition."""
    with open(PathEnums.facetemplate.value, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@router.get("/start")
async def start_recognition():
    """Start the face recognition process and return a result."""
    await rc.start_recognition()  # Assuming start_recognition is asynchronous
    result = await rc.get_recognition_result()  # Fetch the recognition result
    return {"status": "completed", "recognition": result}

@router.get("/result")
async def get_recognition_result():
    """Fetch the recognition result without starting the process."""
    result = await rc.get_recognition_result()
    return {"status": "fetched", "result": result}