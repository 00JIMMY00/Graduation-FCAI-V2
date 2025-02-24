from typing import Dict, Any
import asyncio
import httpx

from fastapi import APIRouter, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from tempfile import NamedTemporaryFile
import shutil
import subprocess
import os

from voice2txt.src.Controllers.SpeechController import SpeechController
from face_recognition2.src.controllers.recognition_controller import RecognitionController
from .pathEnums import PathEnums

# Initialize router
router = APIRouter()

# Initialize controllers
recognition_controller = RecognitionController()
speech_controller = SpeechController()

# Add global variables to hold ongoing tasks
current_face_task = None
current_voice_task = None

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
    return await process_recognition()

@router.post("/start")
async def handle_audio(
    audio: UploadFile = File(...),
    name: str = Form(...),
    user_type: str = Form(...),
    class_type: str = Form(..., alias="class")
):
    # Temporary file paths
    webm_path = None
    wav_path = None
    
    try:
        # Save uploaded webm file
        with NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
            shutil.copyfileobj(audio.file, temp_webm)
            webm_path = temp_webm.name

        # Convert to WAV using ffmpeg
        wav_path = webm_path.replace('.webm', '.wav')
        try:
            result = subprocess.run([
                'ffmpeg',
                '-i', webm_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                wav_path
            ], check=True, capture_output=True)
            print("Audio conversion successful")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise Exception(f"Failed to convert audio: {e.stderr.decode()}")

        # Process the converted WAV file
        speech_result = await speech_controller.process_speech(wav_path)
        
        # Create recognition result
        recognition_result = {
            "name": name,
            "user_type": user_type,
            "class": class_type,
            "message": speech_result.get("text", "No speech detected")
        }

        # Send to chat API
        chat_api_url = "https://primary-production-5212.up.railway.app/webhook/chat/message"
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(
                chat_api_url,
                json=recognition_result,
                headers=headers
            )
            chat_result = chat_response.json()
            
            final_result = {
                "recognition": recognition_result,
                "chat_response": chat_result
            }

            if chat_result.get("error"):
                final_result["chat_error"] = chat_result["error"]

            return JSONResponse(
                content=final_result,
                headers=get_response_headers()
            )

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return create_error_response(
            message="Failed to process audio",
            details=str(e)
        )
    finally:
        # Cleanup temporary files
        for path in [webm_path, wav_path]:
            if path and os.path.exists(path):
                import os
                try:
                    os.unlink(path)
                except Exception as e:
                    print(f"Error deleting temporary file {path}: {e}")

    try:
        # Process the audio file with speech recognition
        speech_result = await speech_controller.process_speech(temp_file_path)
        
        # Create recognition result with the provided user info
        recognition_result = {
            "name": name,
            "user_type": user_type,
            "class": class_type,
            "message": speech_result.get("text", "No speech detected")
        }

        # Send to chat API
        chat_api_url = "https://primary-production-5212.up.railway.app/webhook/chat/message"
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(
                chat_api_url,
                json=recognition_result,
                headers=headers
            )
            chat_result = chat_response.json()
            
            # Format the final response
            final_result = {
                "recognition": recognition_result,
                "chat_response": chat_result
            }

            if chat_result.get("error"):
                final_result["chat_error"] = chat_result["error"]

            return JSONResponse(
                content=final_result,
                headers=get_response_headers()
            )

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return create_error_response(
            message="Failed to process audio",
            details=str(e)
        )
    finally:
        # Cleanup temporary file
        import os
        try:
            os.unlink(temp_file_path)
        except:
            pass

async def process_recognition():
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

# Modified /start endpoint to begin concurrent recognition without awaiting their completion
@router.get("/start", response_class=HTMLResponse)
async def start_recording():
    global current_face_task, current_voice_task
    current_face_task = asyncio.create_task(recognition_controller.start_recognition())
    current_voice_task = asyncio.create_task(speech_controller.process_speech())
    return {
        "status": "recording started",
        "instruction": "Speak now (Supported languages: ar-EG, en-US)..."
    }

# New /stop endpoint to stop recording, gather results and send them to the RAG API
@router.get("/stop")
async def stop_recording():
    global current_face_task, current_voice_task
    if current_face_task is None or current_voice_task is None:
        return create_error_response("No active recording to stop")
    
    try:
        # Await both tasks to complete
        face_result = await current_face_task
        voice_result = await current_voice_task
    except Exception as e:
        return create_error_response("Error during recognition", details=str(e))
    finally:
        current_face_task = None
        current_voice_task = None

    # Compose the recognition result based on available data
    recognition_result = {
        "name": face_result.get("name", "Unknown"),
        "user_type": face_result.get("user_type", "student"),
        "class": face_result.get("class", "N/A"),
        "message": voice_result.get("text", "No speech detected")
    }

    # Send recognition result to the RAG API endpoint
    chat_api_url = "https://primary-production-5212.up.railway.app/webhook/chat/message"
    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(chat_api_url, json=recognition_result, headers=headers)
            chat_result = chat_response.json()
        final_result = {
            "recognition": recognition_result,
            "chat_response": chat_result,
            "timestamp": chat_result.get("timestamp", None)
        }
        if "error" in chat_result:
            final_result["chat_error"] = chat_result["error"]
        return final_result
    except Exception as e:
        return create_error_response("Chat API error", details=str(e))




