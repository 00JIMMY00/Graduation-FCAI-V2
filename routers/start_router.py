from typing import Dict, Any
import asyncio
import httpx

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from voice2txt.src.Controllers.SpeechController import SpeechController
from face_recognition2.src.controllers.recognition_controller import RecognitionController
from .pathEnums import PathEnums

# Initialize router
router = APIRouter()

# Initialize controllers
recognition_controller = RecognitionController()
speech_controller = SpeechController()

def get_response_headers() -> Dict[str, str]:
    """Get common response headers with CORS settings."""
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

def create_error_response(message: str, details: Any = None) -> JSONResponse:
    """Create a standardized error response."""
    content = {"error": message}
    if details:
        content["details"] = details
    return JSONResponse(content=content, headers=get_response_headers())
@router.get("/", response_class=HTMLResponse)
async def vf_starting_page():
    #Serve the HTML page for face recognition and voice2txt.
    with open(PathEnums.voicefacestart.value, "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)



@router.get("/start")
async def start_processing():
    """Run face recognition and voice processing concurrently."""
    # Start the face recognition and voice processing concurrently
    try:
        result_f, result_v = await asyncio.gather(
            recognition_controller.start_recognition(),   # Face recognition
            speech_controller.process_speech(),      # Speech recognition
            return_exceptions=True    # Don't let one failure stop the other
        )
        
        # Initialize result dict
        recognition_result = {}
        
        # Handle face recognition result
        if isinstance(result_f, Exception):
            print(f"Face recognition error: {str(result_f)}")
            recognition_result["face_error"] = "Failed to capture face recognition"
            return create_error_response(
                message="Face recognition failed",
                details=str(result_f) if isinstance(result_f, Exception) else None
            )
        elif result_f is None:
            recognition_result["face_error"] = "No face detected"
            return create_error_response(
                message="No face detected",
                details="Face detection failed to identify any faces in the image"
            )
            
        # Handle speech recognition result
        if isinstance(result_v, Exception):
            print(f"Speech recognition error: {str(result_v)}")
            recognition_result["speech_error"] = "Failed to capture speech"
            return create_error_response(
                message="Speech recognition failed",
                details=str(result_v) if isinstance(result_v, Exception) else None
            )
        elif not result_v or "text" not in result_v:
            recognition_result = {
                "name": result_f["name"],
                "user_type": 'staff' if result_f["class"].lower() in ['doctor', 'dean'] else 'student',
                "class": result_f["class"],
                "speech_error": "No speech detected",
                "message": "No speech input"  # Default message when no speech is detected
            }
        else:
            recognition_result = {
                "name": result_f["name"],
                "user_type": 'staff' if result_f["class"].lower() in ['doctor', 'dean'] else 'student',
                "class": result_f["class"],
                "message": result_v["text"]
            }
        
        # Send to chat API
        chat_api_url = "https://primary-production-5212.up.railway.app/webhook/chat/message"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient() as client:
                chat_response = await client.post(
                    chat_api_url,
                    json=recognition_result,
                    headers=headers
                )
                chat_result = chat_response.json()
                
                # Format the final response
                final_result = {
                    "recognition": {
                        "name": recognition_result["name"],
                        "user_type": recognition_result["user_type"],
                        "message": recognition_result["message"]
                    }
                }

                # Add chat response if available
                if chat_result:
                    final_result["chat_response"] = chat_result

                
                if "speech_error" in recognition_result:
                    final_result["recognition"]["speech_error"] = recognition_result["speech_error"]
                
                # Process chat result
                final_result["timestamp"] = chat_result.get("timestamp", None)
                if "error" in chat_result:
                    final_result["chat_error"] = chat_result["error"]

                return JSONResponse(
                    content=final_result,
                    headers=get_response_headers()
                )
                
        except Exception as e:
            error_msg = str(e)
            print(f"Chat API error: {error_msg}")
            return JSONResponse(
                content={
                    "recognition": {
                        "name": recognition_result["name"],
                        "user_type": recognition_result["user_type"],
                        "message": recognition_result["message"],
                        "speech_error": recognition_result.get("speech_error")
                    },
                    "chat_error": error_msg
                },
                headers=get_response_headers()
            )
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return create_error_response(
            message="Processing failed",
            details=str(e)
        )

@router.get("/result")
async def get_recognition_result():
    """Fetch the recognition result without starting the process."""
    result = await recognition_controller.get_recognition_result()
    return {"status": "fetched", "result": result}




