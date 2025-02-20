from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers.face_routers import router as face_router
from routers.voice_routes import router as voice_router
import uvicorn
from pathlib import Path

app = FastAPI()

# Include the routers
app.include_router(face_router, prefix="/face")
app.include_router(voice_router, prefix="/voice")

@app.get("/home/", response_class=HTMLResponse)
async def home_page():
    # Path to the home.html file
    home_template_path = Path("templates/home.html")
    # Return the file as an HTMLResponse
    return HTMLResponse(content=home_template_path.read_text())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)