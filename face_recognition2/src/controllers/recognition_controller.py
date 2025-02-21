import cv2
from ..models import FacialRecognitionModel
from ..helpers import get_settings
import json
import asyncio

class RecognitionController:
    def __init__(self):
        """Initialize the RecognitionController class."""
    
        self.result = None
        self.model = None
        self.camera = None

    async def initialize_camera(self):
        """Initialize the camera and model."""
        # Always close any existing camera first
        if self.camera is not None:
            print("Releasing existing camera...")
            self.camera.release()
            await asyncio.sleep(1.0)  # Wait for clean release
            
        # Try different camera indices
        for camera_index in range(4):  # Try indices 0-3
            print(f"Attempting to initialize camera with index {camera_index}...")
            try:
                # Try different camera backends
                backends = [
                    (cv2.CAP_DSHOW, "DirectShow"),
                    (cv2.CAP_ANY, "Default"),
                    (0, "Fallback")  # Simple index-based fallback
                ]
                
                for backend, name in backends:
                    try:
                        print(f"Trying {name} backend for camera {camera_index}...")
                        if backend == 0:  # Fallback method
                            self.camera = cv2.VideoCapture(camera_index)
                        else:
                            self.camera = cv2.VideoCapture(camera_index, backend)
                            
                        if self.camera.isOpened():
                            print(f"Successfully opened camera {camera_index} with {name} backend")
                            break
                        else:
                            print(f"{name} backend failed for camera {camera_index}")
                            self.camera.release()
                    except Exception as e:
                        print(f"Error with {name} backend: {str(e)}")
                        if self.camera:
                            self.camera.release()
                        continue
                if not self.camera.isOpened():
                    print(f"Failed to open camera {camera_index}")
                    continue

                # Configure camera settings
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set reasonable resolution
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                # Let the camera warm up
                print(f"Camera {camera_index} opened, warming up...")
                await asyncio.sleep(2.0)  # Extended warm-up time

                # Test capture multiple times
                for attempt in range(3):
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        print(f"Successfully connected to camera {camera_index}")
                        return True
                    print(f"Capture attempt {attempt + 1} failed for camera {camera_index}")
                    await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error initializing camera {camera_index}: {str(e)}")
            finally:
                if self.camera and not ret:
                    self.camera.release()
                    await asyncio.sleep(0.5)
        
        print("Error: Could not access any camera. Please ensure a camera is connected and not in use by another application.")
        return False

    async def start_recognition(self):
        """Capture a single frame and perform recognition."""
        try:
            print("Starting face recognition process...")
            if self.model is None:
                print("Initializing facial recognition model...")
                try:
                    self.model = await FacialRecognitionModel.Init_FacialRecognitionModel()
                except Exception as e:
                    print(f"Error initializing model: {str(e)}")
                    raise Exception(f"Failed to initialize facial recognition model: {str(e)}")

            # Initialize camera
            print("Attempting to initialize camera...")
            if not await self.initialize_camera():
                raise Exception("Failed to initialize any available camera. Please check camera connections.")

            # Try to capture frame multiple times if needed
            ret = False
            frame = None
            print("Attempting to capture frame...")
            for attempt in range(3):
                try:
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        print(f"Successfully captured frame on attempt {attempt + 1}")
                        break
                    print(f"Frame capture attempt {attempt + 1} failed")
                    await asyncio.sleep(0.5)  # Increased delay between attempts
                except Exception as e:
                    print(f"Error during frame capture attempt {attempt + 1}: {str(e)}")
                    if attempt == 2:  # Last attempt
                        raise Exception(f"Frame capture failed after 3 attempts: {str(e)}")
            
            if not ret or frame is None:
                raise Exception("Failed to capture valid frame after multiple attempts")

            # Process the frame
            print("Processing captured frame...")
            try:
                self.result = await self.model.predict(frame)
                if self.result is None:
                    raise Exception("Model prediction returned None")
                print("Successfully processed frame")
                return self.result
            except Exception as e:
                print(f"Error during frame processing: {str(e)}")
                raise Exception(f"Failed to process frame: {str(e)}")

        except Exception as e:
            print(f"Error in start_recognition: {str(e)}")
            raise

        finally:
            # Always release the camera
            if self.camera is not None:
                print("Releasing camera...")
                self.camera.release()
                self.camera = None

    async def get_recognition_result(self):
        print("hello from get_recognition_result")
        recognition_result = {
            "class": self.result["class"],
            "name": self.result["name"],
            "confidence": self.result["confidence"]
        }
        print("recognition_result", recognition_result)
        return recognition_result